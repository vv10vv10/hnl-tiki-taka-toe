import { Component, OnInit, OnDestroy } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { GameService } from './services/game.service';
import { GameResponse, Cell, Rule, MatchSummary } from './models/game.model';
import { FormsModule } from '@angular/forms';

interface CategoryOption {
  key: string;
  label: string;
  locked?: boolean;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit, OnDestroy {
  // mora se poklapati s RULE_TYPES u backend/game/views.py
  availableCategories: CategoryOption[] = [
    { key: 'club', label: 'Klub', locked: true },
    { key: 'country', label: 'Reprezentacija' },
    { key: 'confederation', label: 'Konfederacija' },
    { key: 'coach', label: 'Trener' },
    { key: 'hnl_nastupi', label: 'HNL nastupi' },
    { key: 'hnl_golovi', label: 'HNL golovi' },
  ];

  selectedCategories: Record<string, boolean> = {
    club: true,
    country: true,
    confederation: true,
    coach: true,
    hnl_nastupi: true,
    hnl_golovi: true,
  };

  showCategorySelector = true;

  // 'single' = obicna igra, '3'/'5' = best of serija
  matchMode: 'single' | '3' | '5' = 'single';
  matchId: string | null = null;
  matchInfo: MatchSummary | null = null;
  autoAdvanceTimer: ReturnType<typeof setTimeout> | null = null;

  // play with a friend (online preko linka)
  onlineEnabled = false;
  onlineSecondsPerMove = 60;
  isFriendMode = false;
  friendLink: string | null = null;
  mySession: string | null = null;
  mySymbol: string | null = null;
  waitingForOpponent = false;
  secondsRemaining: number | null = null;
  private pollingInterval: ReturnType<typeof setInterval> | null = null;

  get selectedCategoryKeys(): string[] {
    return Object.entries(this.selectedCategories)
      .filter(([_, checked]) => checked)
      .map(([key]) => key);
  }

  get canStartGame(): boolean {
    return this.selectedCategoryKeys.length >= 2;
  }

  get isMyTurn(): boolean {
    return this.mySymbol === this.currentTurn;
  }

  toggleCategory(key: string) {
    const cat = this.availableCategories.find(c => c.key === key);
    if (cat?.locked) return;
    this.selectedCategories[key] = !this.selectedCategories[key];
  }

  openCategorySelector() {
    this.clearAutoAdvance();
    this.stopPolling();
    this.showCategorySelector = true;
    this.matchId = null;
    this.matchInfo = null;
    this.matchMode = 'single';
    this.isFriendMode = false;
    this.friendLink = null;
    this.mySession = null;
    this.mySymbol = null;
    this.waitingForOpponent = false;
    this.secondsRemaining = null;
    this.onlineEnabled = false;
  }

  gameId: string | null = null;
  board: Cell[][] = [];
  selectedPlayer = "Filip Bradarić";
  currentTurn:string | null = null;
  isFinished = false;
  winner: string | null = null;
  rowRules: Rule[] = [];
  colRules: Rule[] = [];
  showInvalidMoveFeedback = false;
  winningLine: number[][] | null = null;
  selectedCell: { row: number, col: number } | null = null;
  players: any[] = [];
  filteredPlayers: any[] = [];
  playersLoadError = false;
  possiblePlayers: any[] = [];
  searchTerm: string = "";
  showPicker = false;
  showPossiblePlayersModal = false;
  lineCoords = {x1: 0,y1: 0,x2: 0,y2: 0};

  constructor(private gameService: GameService) {}

  ngOnInit() {
    this.gameService.getPlayers().subscribe(res => {
      this.players = res;
      this.filteredPlayers = res;
    });

    const match = window.location.pathname.match(/\/match\/([0-9a-fA-F-]{36})/);
    if (match) {
      this.joinFriendMatch(match[1]);
    }
  }

  ngOnDestroy() {
    this.stopPolling();
  }

  onStartClick() {
    if (!this.canStartGame) return;
    if (this.onlineEnabled) {
      this.startFriendMatch();
      return;
    }
    if (this.matchMode === 'single') {
      this.createGame();
    } else {
      this.createMatchSeries(parseInt(this.matchMode, 10));
    }
  }

  createGame() {
    this.clearAutoAdvance();
    this.gameService.createGame(this.selectedCategoryKeys).subscribe((res: GameResponse) => {
      this.gameId = res.game_id;
      this.matchId = null;
      this.matchInfo = null;
      this.isFinished = false;
      this.winner = null;
      this.winningLine = null;
      this.currentTurn = "X";
      this.showCategorySelector = false;
      this.loadGame();
    });
  }

  createMatchSeries(bestOf: number) {
    this.clearAutoAdvance();
    this.gameService.createMatch(bestOf, this.selectedCategoryKeys).subscribe(res => {
      this.matchId = res.match.match_id;
      this.matchInfo = res.match;
      this.gameId = res.game_id;
      this.isFinished = false;
      this.winner = null;
      this.winningLine = null;
      this.currentTurn = "X";
      this.showCategorySelector = false;
      this.loadGame();
    });
  }

  startFriendMatch() {
    if (!this.canStartGame) return;
    this.clearAutoAdvance();
    const bestOf = this.matchMode === 'single' ? 1 : parseInt(this.matchMode, 10);
    this.gameService.createMatch(bestOf, this.selectedCategoryKeys, true, this.onlineSecondsPerMove)
      .subscribe(res => {
        this.isFriendMode = true;
        this.matchId = res.match.match_id;
        this.matchInfo = res.match;
        this.gameId = res.game_id;
        this.mySession = res.your_session ?? null;
        this.mySymbol = res.your_symbol ?? null;
        if (this.mySession && this.matchId) {
          localStorage.setItem(`ttt-session-${this.matchId}`, this.mySession);
        }
        this.friendLink = `${window.location.origin}/match/${this.matchId}`;
        this.isFinished = false;
        this.winner = null;
        this.winningLine = null;
        this.showCategorySelector = false;
        this.waitingForOpponent = true;
        this.startPolling();
      });
  }

  joinFriendMatch(matchId: string) {
    this.isFriendMode = true;
    this.showCategorySelector = false;
    const storedSession = localStorage.getItem(`ttt-session-${matchId}`);
    this.gameService.joinMatch(matchId, storedSession || undefined).subscribe(res => {
      this.matchId = matchId;
      this.mySession = res.your_session;
      this.mySymbol = res.your_symbol;
      localStorage.setItem(`ttt-session-${matchId}`, res.your_session);
      this.matchInfo = res.match;
      this.startPolling();
    });
  }

  copyFriendLink() {
    if (!this.friendLink) return;
    navigator.clipboard.writeText(this.friendLink);
  }

  startPolling() {
    this.stopPolling();
    this.pollMatchState();
    this.pollingInterval = setInterval(() => this.pollMatchState(), 1500);
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  pollMatchState() {
    if (!this.matchId) return;
    this.gameService.getMatchState(this.matchId, this.mySession || undefined).subscribe(res => {
      this.gameId = res.game_id;
      this.board = res.board;
      this.rowRules = res.row_rules;
      this.colRules = res.col_rules;
      this.currentTurn = res.current_turn;
      this.isFinished = res.is_finished;
      this.winner = res.winner;
      this.winningLine = res.winning_line;
      this.matchInfo = res.match;
      this.waitingForOpponent = res.waiting_for_opponent;
      this.secondsRemaining = res.seconds_remaining;
      if (res.your_symbol) {
        this.mySymbol = res.your_symbol;
      }
      if (this.winningLine) {
        this.updateWinningLine();
      }
      if (res.match.is_finished) {
        this.stopPolling();
      }
    });
  }

  confirmNextGame() {
    if (!this.matchId) return;
    if (this.winner) {
      // igra je vec zavrsena, nema sto izgubiti - odmah idi dalje bez potvrde
      this.clearAutoAdvance();
      this.nextGame();
      return;
    }
    const confirmed = window.confirm(
      'Igra će se zabilježiti kao remi, a krenut će sljedeća igra u seriji. Jeste li sigurni?'
    );
    if (!confirmed) return;
    this.clearAutoAdvance();
    this.nextGame();
  }

  scheduleAutoNextGame() {
    this.clearAutoAdvance();
    this.autoAdvanceTimer = setTimeout(() => {
      this.autoAdvanceTimer = null;
      this.nextGame();
    }, 2500);
  }

  clearAutoAdvance() {
    if (this.autoAdvanceTimer) {
      clearTimeout(this.autoAdvanceTimer);
      this.autoAdvanceTimer = null;
    }
  }

  nextGame() {
    this.clearAutoAdvance();
    if (!this.matchId) return;
    this.gameService.nextGame(this.matchId).subscribe(res => {
      this.gameId = res.game_id;
      this.matchInfo = res.match;
      this.isFinished = false;
      this.winner = null;
      this.winningLine = null;
      this.currentTurn = "X";
      if (this.isFriendMode) {
        // sljedeci poll ce pokupiti novi game preko match state-a
        return;
      }
      this.loadGame();
    });
  }

  loadGame() {
    if (!this.gameId) return;
    this.gameService.getGame(this.gameId).subscribe((res:GameResponse) => {
      this.board = res.board;
      this.currentTurn = res.current_turn;
      this.winner = res.winner;
      this.rowRules = res.row_rules;
      this.colRules = res.col_rules;
      this.winningLine = res.winning_line;
      if (res.match) {
        this.matchInfo = res.match;
        this.matchId = res.match_id ?? this.matchId;
      }
    });
  }

  onCellClick(row: number, col: number) {
    if (this.isFinished) {
      this.showPossiblePlayers(row, col);
      return;
    }
    if (this.isFriendMode && (this.waitingForOpponent || !this.isMyTurn)) {
      return;
    }
    const cell = this.board[row][col];
    if (!cell.symbol) {
      this.selectedCell = { row, col };
      this.showPicker = true;
      this.searchTerm = "";
      this.filteredPlayers = this.players;
    }
  }

  updateWinningLine() {
    if (!this.winningLine) return;

    const first = this.winningLine[0];
    const last = this.winningLine[2];

    this.lineCoords = {
      x1: first[1] * 60 + 30,
      y1: first[0] * 60 + 30,
      x2: last[1] * 60 + 30,
      y2: last[0] * 60 + 30,
    };
  }

  onSearchChange(value: string) {
    this.filteredPlayers = this.players.filter(p =>
      this.normalize(p.name).includes(this.normalize(value)) ||
      this.normalize(p.name_in_home_country).includes(this.normalize(value)) ||
      this.normalize(p.search_name).includes(this.normalize(value))
    );
  }

  normalize(text: string): string {
    return text
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  }

  selectPlayer(player: any) {
    if (!this.selectedCell || !this.gameId) return;

    this.gameService.playMove({
      game_id: this.gameId,
      row: this.selectedCell.row,
      col: this.selectedCell.col,
      player_name: player.name,
      session: this.mySession || undefined
    }).subscribe(res => {
      if (res.valid) {
        this.board = res.board;
        this.currentTurn = res.current_turn;
        this.isFinished = res.is_finished;
        this.winner = res.winner;
        this.winningLine = res.winning_line;
        if (res.match) {
          this.matchInfo = res.match;
        }
        if (this.winningLine) {
          this.updateWinningLine();
        }
        if (res.is_finished && res.match && !res.match.is_finished) {
          // u friend modu samo X (kreator) automatski pokrece sljedecu igru,
          // da ne dodje do dvostrukog poziva kad oba klijenta reagiraju na kraj
          if (!this.isFriendMode || this.mySymbol === 'X') {
            this.scheduleAutoNextGame();
          }
        }
      } else {
        this.currentTurn = this.currentTurn === 'X' ? 'O' : 'X';
        this.showInvalidMoveFeedback = true;
        setTimeout(() => {
          this.showInvalidMoveFeedback = false;
        }, 600);
      }

      this.showPicker = false;
      this.selectedCell = null;
    });
  }

  showPossiblePlayers(row: number, col: number) {
    if (!this.gameId) {
      return;
    }
    this.gameService
      .getPossiblePlayers(this.gameId, row, col)
      .subscribe(players => {
        this.possiblePlayers = players;
        this.showPossiblePlayersModal = true;
      });
  }
}