import { Component } from '@angular/core';
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
export class AppComponent {
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

  get selectedCategoryKeys(): string[] {
    return Object.entries(this.selectedCategories)
      .filter(([_, checked]) => checked)
      .map(([key]) => key);
  }

  get canStartGame(): boolean {
    return this.selectedCategoryKeys.length >= 2;
  }

  toggleCategory(key: string) {
    const cat = this.availableCategories.find(c => c.key === key);
    if (cat?.locked) return;
    this.selectedCategories[key] = !this.selectedCategories[key];
  }

  openCategorySelector() {
    this.clearAutoAdvance();
    this.showCategorySelector = true;
    this.matchId = null;
    this.matchInfo = null;
    this.matchMode = 'single';
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

  onStartClick() {
    if (!this.canStartGame) return;
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

  ngOnInit() {
    this.gameService.getPlayers().subscribe(res => {
      this.players = res;
      this.filteredPlayers = res;
    });
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
      player_name: player.name
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
          this.scheduleAutoNextGame();
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