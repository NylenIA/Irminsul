import { prisma } from "./client";
import {
  PrismaSqliteTeamRepository,
  type TeamRepository,
} from "./repositories/team-repository";

export { prisma } from "./client";
export {
  PrismaSqliteTeamRepository,
  TeamRepositoryValidationError,
  type TeamRepository,
  type SaveTeamInput,
  type SavedTeamDTO,
  type TeamMemberInput,
} from "./repositories/team-repository";
export { EXPECTED_MIGRATIONS } from "./expected-migrations";
export {
  checkSchemaDrift,
  type SchemaDriftReport,
  type SchemaDriftStatus,
  type RawQueryClient,
} from "./schema-drift";

/** Fabrique serveur du repository d'équipes (singleton Prisma). À n'importer QUE côté serveur. */
export function getTeamRepository(): TeamRepository {
  return new PrismaSqliteTeamRepository(prisma);
}
