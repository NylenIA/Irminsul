// Interface de persistance indépendante du backend (Prisma maintenant, Supabase plus tard).
// L'UI dépend de CETTE interface, jamais du schéma Prisma directement.
import type { PrismaClient } from "@prisma/client";

export interface TeamMemberInput {
  character: string;
  role?: string | null;
  slot: number;
}

export interface SaveTeamInput {
  name: string;
  carry?: string | null;
  notes?: string | null;
  members: TeamMemberInput[];
}

export interface SavedTeamDTO {
  id: string;
  name: string;
  carry: string | null;
  notes: string | null;
  members: { character: string; role: string | null; slot: number }[];
}

export interface TeamRepository {
  save(input: SaveTeamInput): Promise<SavedTeamDTO>;
  list(): Promise<SavedTeamDTO[]>;
  getById(id: string): Promise<SavedTeamDTO | null>;
  delete(id: string): Promise<void>;
}

interface TeamRow {
  id: string;
  name: string;
  carry: string | null;
  notes: string | null;
  members: { character: string; role: string | null; slot: number }[];
}

function toDTO(team: TeamRow): SavedTeamDTO {
  return {
    id: team.id,
    name: team.name,
    carry: team.carry,
    notes: team.notes,
    members: team.members.map((m) => ({
      character: m.character,
      role: m.role,
      slot: m.slot,
    })),
  };
}

/** Implémentation LOCAL-FIRST (SQLite via Prisma). */
export class PrismaSqliteTeamRepository implements TeamRepository {
  constructor(private readonly db: PrismaClient) {}

  async save(input: SaveTeamInput): Promise<SavedTeamDTO> {
    const team = await this.db.savedTeam.create({
      data: {
        name: input.name,
        carry: input.carry ?? null,
        notes: input.notes ?? null,
        members: {
          create: input.members.map((m) => ({
            character: m.character,
            role: m.role ?? null,
            slot: m.slot,
          })),
        },
      },
      include: { members: { orderBy: { slot: "asc" } } },
    });
    return toDTO(team);
  }

  async list(): Promise<SavedTeamDTO[]> {
    const teams = await this.db.savedTeam.findMany({
      include: { members: { orderBy: { slot: "asc" } } },
      orderBy: { updatedAt: "desc" },
    });
    return teams.map(toDTO);
  }

  async getById(id: string): Promise<SavedTeamDTO | null> {
    const team = await this.db.savedTeam.findUnique({
      where: { id },
      include: { members: { orderBy: { slot: "asc" } } },
    });
    return team ? toDTO(team) : null;
  }

  async delete(id: string): Promise<void> {
    await this.db.savedTeam.delete({ where: { id } });
  }
}
