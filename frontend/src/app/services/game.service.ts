import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import {
  GameResponse,
  CreateMatchResponse,
  MatchSummary,
  JoinMatchResponse,
  MatchStateResponse
} from '../models/game.model';

@Injectable({
  providedIn: 'root'
})
export class GameService {

  private http = inject(HttpClient);

  private api = environment.apiUrl;

  createGame(categories?: string[]) {
    const body = categories && categories.length ? { categories } : {};
    return this.http.post<GameResponse>(`${this.api}/create-game/`, body);
  }

  createMatch(bestOf: number, categories?: string[], online?: boolean, secondsPerMove?: number) {
    const body: any = { best_of: bestOf };
    if (categories && categories.length) {
      body.categories = categories;
    }
    if (online) {
      body.online = true;
      body.seconds_per_move = secondsPerMove;
    }
    return this.http.post<CreateMatchResponse>(`${this.api}/create-match/`, body);
  }

  getMatch(matchId: string) {
    return this.http.get<MatchSummary>(`${this.api}/match/${matchId}/`);
  }

  joinMatch(matchId: string, session?: string) {
    return this.http.post<JoinMatchResponse>(`${this.api}/match/${matchId}/join/`, { session });
  }

  joinByCode(code: string, session?: string) {
    return this.http.post<JoinMatchResponse>(`${this.api}/join-by-code/`, { code, session });
  }

  getMatchState(matchId: string, session?: string) {
    const query = session ? `?session=${session}` : '';
    return this.http.get<MatchStateResponse>(`${this.api}/match/${matchId}/state/${query}`);
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

  getPlayersMeta() {
    return this.http.get<{ last_updated: string }>(`${this.api}/players-meta/`);
  }

  playMove(data: {
    game_id: string;
    row: number;
    col: number;
    player_name: string;
    session?: string;
  }) {
    return this.http.post<any>(`${this.api}/play-move/`, data);
  }

  getPossiblePlayers(gameId: string, row: number, col: number) {
    return this.http.get<any[]>(
      `${this.api}/game/${gameId}/possible-players/?row=${row}&col=${col}`
    );
  }

  requestDraw(gameId: string, data: { symbol: string; session?: string }) {
    return this.http.post<{ draw_requested_by: string | null }>(
      `${this.api}/game/${gameId}/request-draw/`, data
    );
  }

  respondDraw(gameId: string, data: { accept: boolean; symbol: string; session?: string }) {
    return this.http.post<{ is_finished: boolean; winner: string | null; draw_requested_by: string | null }>(
      `${this.api}/game/${gameId}/respond-draw/`, data
    );
  }

  passTurn(gameId: string, data: { symbol: string; session?: string }) {
    return this.http.post<{ current_turn: string }>(
      `${this.api}/game/${gameId}/pass-turn/`, data
    );
  }
}