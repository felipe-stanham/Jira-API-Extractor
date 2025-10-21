# Migrations Folder

This folder contains SQL scripts for database schema changes and rollbacks.

## Purpose

Track all database schema changes in version-controlled SQL scripts.

## File Naming Convention

Format: `YYYYMMDD_HHMM_description.sql`

Example: `20250121_1430_add_user_table.sql`

## Script Structure

Each migration script should include:

```sql
-- Migration: [Description]
-- Date: [YYYY-MM-DD]
-- Author: [Name]

-- ==================================================
-- UP Migration
-- ==================================================

-- Your schema changes here
CREATE TABLE example (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- ==================================================
-- DOWN Migration (Rollback)
-- ==================================================

-- Rollback commands here
-- DROP TABLE example;
```

## Best Practices

1. **Always include rollback commands** (commented out)
2. **Test migrations** on development environment first
3. **Keep migrations atomic** - one logical change per file
4. **Document breaking changes** clearly
5. **Include indexes** and constraints in the same migration
6. **Backup data** before running migrations in production

## Migration Types

- **Schema Changes**: CREATE, ALTER, DROP tables/columns
- **Data Migrations**: INSERT, UPDATE, DELETE data
- **Index Changes**: CREATE, DROP indexes
- **Constraint Changes**: ADD, DROP constraints

## Workflow

1. Create migration script with descriptive name
2. Write UP migration (schema changes)
3. Write DOWN migration (rollback)
4. Test on development database
5. Review and commit
6. Apply to production with backup

## Status

Currently empty - this project uses Excel files instead of a traditional database.

If the project moves to a database backend in the future, migration scripts will be stored here.

## Future Considerations

If implementing a database:
- Consider using a migration tool (Alembic, Flyway, Liquibase)
- Track applied migrations in a `schema_migrations` table
- Implement automated migration testing
- Set up migration CI/CD pipeline
