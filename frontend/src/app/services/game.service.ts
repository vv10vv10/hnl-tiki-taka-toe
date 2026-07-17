import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { GameResponse, CreateMatchResponse, MatchSummary } from '../models/game.model';

@Injectable({
  providedIn: 'root'
})
export class GameService {

  private http = inject(HttpClient);

  private api = 'http://127.0.0.1:8000/api';

  createGame(categories?: string[]) {
    const body = categories && categories.length ? { categories } : {};
    return this.http.post<GameResponse>(`${this.api}/create-game/`, body);
  }

  createMatch(bestOf: number, categories?: string[]) {
    const body: any = { best_of: bestOf };
    if (categories && categories.length) {
      body.categories = categories;
    }
    return this.http.post<CreateMatchResponse>(`${this.api}/create-match/`, body);
  }

  getMatch(matchId: string) {
    return this.http.get<MatchSummary>(`${this.api}/match/${matchId}/`);
  }

  nextGame(matchId: string) {
    return this.http.post<CreateMatchResponse>(`${this.api}/next-game/`, { match_id: matchId });
  }

  getGame(gameId: string) {
    return this.http.get<GameResponse>(`${this.api}/game/${gameId}/`);
  }

  getPlayers() {
    return this.http.get<any[]>(`${this.api}/players/`);
  }

  playMove(data: {
    game_id: string;
    row: number;
    col: number;
    player_name: string;
  }) {
    return this.http.post<any>(`${this.api}/play-move/`, data);
  }

  getPossiblePlayers(gameId: string, row: number, col: number) {
    return this.http.get<any[]>(
      `${this.api}/game/${gameId}/possible-players/?row=${row}&col=${col}`
    );
  }
}