# DAK MYGA Intro

This repository contains the source materials for an 8-part actuarial course
introducing the fundamentals of Multi-Year Guaranteed Annuity (MYGA) products.

The course covers product structure, specifications, illustration mechanics,
and introductory reserving concepts, with a focus on deterministic modeling
and Python-based implementation.

## Purpose

This repository serves as the instructor-maintained source of truth for:
- Course structure and content
- Lesson materials and examples
- Assignment templates and reference implementations

Students do not directly contribute to this repository.

## Student Access

Students access course materials through:
- GitHub Pages (lecture content, examples, demos)
- GitHub Classroom (assignments and auto-graded exercises)

This repository itself is not used for student submissions.

## Repository Structure

- `lessons/`  
  Instructor-authored lesson content and supporting materials.

- `assignments/`  
  Assignment templates and problem definitions used to generate
  GitHub Classroom exercises.

- `projects/`  
  Larger milestone-based modeling exercises.

- `docs/`  
  Internal documentation and planning notes.

## Usage Notes

- This repository is maintained privately by the instructor.
- No open-source license is applied; all rights are reserved.
- Python is the primary implementation language.

## Status

This course is under active development.

## Site

The repository previously contained a React/Vite-based `site/` front-end; that has been removed. The project now uses MkDocs to build and publish the documentation site from `lessons/` (see the MkDocs section below).

## MkDocs site (new)

This repository now includes a MkDocs-based site configuration. MkDocs will build static pages from the Markdown files under `lessons/` and publish them to GitHub Pages.

- Local preview:
```bash
python -m pip install -r requirements.txt
mkdocs serve
```

- Build locally:
```bash
mkdocs build -d mkdocs_site
```

- The GitHub Actions workflow `.github/workflows/mkdocs-deploy.yml` builds the site and deploys the `mkdocs_site` folder to the `gh-pages` branch on push to `main`.

Using MkDocs Material theme
--------------------------------
This repository is configured to use the `mkdocs-material` theme for a more polished site. To preview locally with the Material theme and syntax highlighting, run:

```bash
python -m pip install -r requirements.txt
mkdocs serve

# then open http://127.0.0.1:8000
```

Notes:
- If you want to customize the look further (fonts, primary/accent colors, logo), edit `mkdocs.yml` under the `theme:` section.
- If you change `requirements.txt`, re-run the pip install command before serving or building.

Notes about the existing React site:
- The older React-based site remains in the `site/` folder. If you want to fully remove it, I can either delete it or move it to a backup folder (e.g., `site-react-backup`) — tell me which you prefer.


