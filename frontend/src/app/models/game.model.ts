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
}