import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { GameService } from './services/game.service';
import { GameResponse, Cell, Rule } from './models/game.model';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
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
  searchTerm: string = "";
  showPicker = false;

  constructor(private gameService: GameService) {}

  createGame() {
    this.gameService.createGame().subscribe((res: GameResponse) => {
      this.gameId = res.game_id;
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
    });
  }

  /*onCellClick(row: number, col: number) {
    if (!this.gameId) return;

    const cell = this.board[row][col];
    if (cell?.symbol) return;

    this.gameService.playMove({
      game_id: this.gameId,
      row,
      col,
      player_name: this.selectedPlayer
    }).subscribe(res => {
      console.log("Move result:", res);

      if (res.valid) {
        this.board = res.board;
        this.currentTurn = res.current_turn;
        this.isFinished = res.is_finished;
        this.winner = res.winner;
        this.winningLine = res.winning_line;
      } else {
        this.currentTurn = this.currentTurn === 'X' ? 'O' : 'X';
        this.showInvalidMoveFeedback = true;
        setTimeout(() => {
          this.showInvalidMoveFeedback = false;
        }, 600);
      }
    });
  }*/
  onCellClick(row: number, col: number) {
    this.selectedCell = { row, col };
    this.showPicker = true;
    this.searchTerm = "";
    this.filteredPlayers = this.players;
  }

  isWinningCell(row: number, col: number): boolean {
    if (!this.winningLine) return false;

    return this.winningLine.some(
      ([r, c]) => r === row && c === col
    );
  }

  ngOnInit() {
    this.gameService.getPlayers().subscribe(res => {
      this.players = res;
      this.filteredPlayers = res;
    });
  }

  onSearchChange(value: string) {
    this.filteredPlayers = this.players.filter(p =>
      p.name.toLowerCase().includes(value.toLowerCase()) ||
      p.name_in_home_country.toLowerCase().includes(value.toLowerCase())
    );
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
}