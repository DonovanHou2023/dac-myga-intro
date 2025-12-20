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

## Site (React + GitHub Pages)

A small React site is scaffolded under `site/` to serve as a GitHub Pages front-end that can dynamically load lesson markdown.

- Install dependencies inside the `site` folder and run the dev server:

```bash
cd site
npm install
npm run dev
```

- Build for production and deploy to GitHub Pages (configure `homepage` in `site/package.json` first):

```bash
cd site
npm run build
npm run deploy
```

The React app fetches `lessons/01-foundations-review/objectives.md` at runtime. When you click the "Show Objectives" button the markdown is loaded and rendered.

## Continuous Deployment

A GitHub Actions workflow is added to automatically build and deploy the `site/` folder to the `gh-pages` branch whenever you push to `main`.

- The workflow file is: `.github/workflows/deploy.yml`.
- It installs Node, runs `npm ci` and `npm run build` in the `site/` folder, then publishes `site/dist` to `gh-pages` using `peaceiris/actions-gh-pages`.

Notes about auto-refresh:
- After the workflow completes and the `gh-pages` branch is updated, GitHub Pages will serve the new files. Visitors must reload their browser to see changes; you cannot force all clients to auto-refresh on commit. During development, use the Vite dev server (`npm run dev`) for live HMR.

