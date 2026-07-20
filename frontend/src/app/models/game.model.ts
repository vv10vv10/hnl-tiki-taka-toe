export interface Rule {
  index: number;
  field: string;
  value: string;
  display: string
}

export interface Cell {
  symbol: string | null;
  player: string | null;
}

export interface MatchSummary {
  match_id: string;
  best_of: number;
  x_wins: number;
  o_wins: number;
  is_finished: boolean;
  winner: string | null;
  games_played: number;
  is_online?: boolean;
  seconds_per_move?: number | null;
}

export interface GameResponse {
  game_id: string;
  board: Cell[][];
  current_turn: string;
  is_finished: boolean;
  winner: string | null;
  row_rules: Rule[];
  col_rules: Rule[];
  winning_line: number[][] | null;
  match_id?: string | null;
  game_number?: number;
  match?: MatchSummary | null;
}

export interface CreateMatchResponse {
  match: MatchSummary;
  game_id: string;
  your_session?: string;
  your_symbol?: string;
}

export interface JoinMatchResponse {
  your_session: string;
  your_symbol: string;
  match: MatchSummary;
}

export interface MatchStateResponse {
  game_id: string;
  game_number: number;
  board: Cell[][];
  row_rules: Rule[];
  col_rules: Rule[];
  current_turn: string;
  is_finished: boolean;
  winner: string | null;
  winning_line: number[][] | null;
  your_symbol: string | null;
  seconds_remaining: number | null;
  waiting_for_opponent: boolean;
  match: MatchSummary;
}