-- CreateTable
CREATE TABLE "hackathons" (
    "hackathon_id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "org_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "devpost_url" TEXT NOT NULL,
    "start_time" TIMESTAMPTZ(6) NOT NULL,
    "end_time" TIMESTAMPTZ(6) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "hackathons_pkey" PRIMARY KEY ("hackathon_id")
);

-- CreateTable
CREATE TABLE "projects" (
    "project_id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "hackathon_id" UUID NOT NULL,
    "source_url" TEXT NOT NULL,
    "title" TEXT,
    "github_repo_link" TEXT,
    "data" JSONB,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "projects_pkey" PRIMARY KEY ("project_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "hackathons_devpost_url_key" ON "hackathons"("devpost_url");

-- CreateIndex
CREATE UNIQUE INDEX "projects_source_url_key" ON "projects"("source_url");

-- AddForeignKey
ALTER TABLE "projects" ADD CONSTRAINT "projects_hackathon_id_fkey" FOREIGN KEY ("hackathon_id") REFERENCES "hackathons"("hackathon_id") ON DELETE CASCADE ON UPDATE NO ACTION;
