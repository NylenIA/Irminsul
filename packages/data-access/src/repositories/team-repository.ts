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
  rename(id: string, name: string): Promise<SavedTeamDTO>;
  duplicate(id: string): Promise<SavedTeamDTO>;
  delete(id: string): Promise<void>;
}

export class TeamRepositoryValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "TeamRepositoryValidationError";
  }
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
function normalizeOptionalText(value: string | null | undefined): string | null {
  const normalized = value?.trim() ?? "";
  return normalized.length > 0 ? normalized : null;
}

function validateTeamId(id: string): string {
  const normalized = id.trim();
  if (!normalized) {
    throw new TeamRepositoryValidationError("Team id is required.");
  }
  return normalized;
}

function validateSaveTeamInput(input: SaveTeamInput): SaveTeamInput {
  const name = input.name.trim();
  if (!name) {
    throw new TeamRepositoryValidationError("Team name is required.");
  }

  if (input.members.length < 1 || input.members.length > 4) {
    throw new TeamRepositoryValidationError(
      "A saved team must contain between 1 and 4 members.",
    );
  }

  const usedSlots = new Set<number>();
  const usedCharacters = new Set<string>();
  const members = input.members.map((member) => {
    if (!Number.isInteger(member.slot) || member.slot < 0 || member.slot > 3) {
      throw new TeamRepositoryValidationError(
        "Team member slot must be an integer between 0 and 3.",
      );
    }

    if (usedSlots.has(member.slot)) {
      throw new TeamRepositoryValidationError(
        "Team member slots must be unique.",
      );
    }
    usedSlots.add(member.slot);

    const character = member.character.trim();
    if (!character) {
      throw new TeamRepositoryValidationError(
        "Team member character is required.",
      );
    }
    if (usedCharacters.has(character)) {
      throw new TeamRepositoryValidationError(
        "A character cannot occupy two slots in the same team.",
      );
    }
    usedCharacters.add(character);

    return {
      character,
      role: normalizeOptionalText(member.role),
      slot: member.slot,
    };
  });

  return {
    name,
    carry: normalizeOptionalText(input.carry),
    notes: normalizeOptionalText(input.notes),
    members,
  };
}

export class PrismaSqliteTeamRepository implements TeamRepository {
  constructor(private readonly db: PrismaClient) {}

  async save(input: SaveTeamInput): Promise<SavedTeamDTO> {
    const validated = validateSaveTeamInput(input);
    const team = await this.db.savedTeam.create({
      data: {
        name: validated.name,
        carry: validated.carry,
        notes: validated.notes,
        members: {
          create: validated.members.map((m) => ({
            character: m.character,
            role: m.role,
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
    const teamId = validateTeamId(id);
    const team = await this.db.savedTeam.findUnique({
      where: { id: teamId },
      include: { members: { orderBy: { slot: "asc" } } },
    });
    return team ? toDTO(team) : null;
  }

  async rename(id: string, name: string): Promise<SavedTeamDTO> {
    const teamId = validateTeamId(id);
    const newName = name.trim();
    if (!newName) {
      throw new TeamRepositoryValidationError("Team name is required.");
    }
    const existing = await this.db.savedTeam.findUnique({ where: { id: teamId } });
    if (!existing) {
      throw new TeamRepositoryValidationError("Team not found.");
    }
    const team = await this.db.savedTeam.update({
      where: { id: teamId },
      data: { name: newName },
      include: { members: { orderBy: { slot: "asc" } } },
    });
    return toDTO(team);
  }

  async duplicate(id: string): Promise<SavedTeamDTO> {
    const teamId = validateTeamId(id);
    const src = await this.db.savedTeam.findUnique({
      where: { id: teamId },
      include: { members: { orderBy: { slot: "asc" } } },
    });
    if (!src) {
      throw new TeamRepositoryValidationError("Team not found.");
    }
    // Réutilise save() (donc toute la validation) pour la copie.
    return this.save({
      name: `${src.name} (copie)`,
      carry: src.carry,
      notes: src.notes,
      members: src.members.map((m) => ({ character: m.character, role: m.role, slot: m.slot })),
    });
  }

  async delete(id: string): Promise<void> {
    const teamId = validateTeamId(id);
    await this.db.savedTeam.deleteMany({ where: { id: teamId } });
  }
}
