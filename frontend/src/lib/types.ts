export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Paginated<T> {
  items: T[];
  limit: number;
  offset: number;
  count: number;
}

export interface Party {
  id: number;
  ec_id: string | null;
  name: string;
  short_name: string | null;
  electoral_register: string | null;
  collected_at: string;
}

export interface Election {
  id: number;
  name: string;
  election_type: string;
  election_date: string;
  parliament_period: string | null;
  source: string | null;
  collected_at: string;
}

export interface Constituency {
  id: number;
  name: string;
  gss_code: string | null;
  country: string | null;
  valid_from: string | null;
  valid_to: string | null;
  collected_at: string;
}

export interface MemberContact {
  id: number;
  contact_type: string;
  value: string;
  is_primary: boolean;
  collected_at: string;
}

export interface MemberTerm {
  id: number;
  constituency_id: number | null;
  party_id: number | null;
  house: string;
  start_date: string | null;
  end_date: string | null;
  collected_at: string;
}

export interface Member {
  id: number;
  parliament_member_id: number | null;
  name: string;
  display_name: string | null;
  gender: string | null;
  is_current: boolean;
  collected_at: string;
}

export interface MemberDetail extends Member {
  contacts: MemberContact[];
  terms: MemberTerm[];
}

export interface ElectionResult {
  id: number;
  election_id: number;
  constituency_id: number;
  party_id: number | null;
  member_id: number | null;
  candidate_name: string;
  votes: number | null;
  vote_share: number | null;
  is_elected: boolean;
  collected_at: string;
}

export interface Manifesto {
  id: number;
  party_id: number;
  election_id: number | null;
  title: string;
  source_url: string | null;
  published_at: string | null;
  collected_at: string;
}

export interface ManifestoDetail extends Manifesto {
  text: string | null;
}
