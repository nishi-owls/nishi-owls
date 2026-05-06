# CLAUDE.md - Project Guide for AI Assistants

## Project Overview

Official website for Tokyo Metropolitan Nishi High School American Football Team "OWLS" (都立西高アメリカンフットボール部 OWLS).

**Website URL**: https://www.nishi-owls.com
**Deployment**: GitHub Pages (primary, nishi-owls.com) / Netlify (secondary, preview)

## Project Structure

```
/
├── _config.yml           # Main Jekyll configuration
├── _layouts/             # Page templates
├── _includes/            # Reusable template components
├── _sass/                # Modular SCSS stylesheets
├── _data/                # YAML/CSV data files for dynamic content
├── _games/               # Game result pages (organized by year)
├── _game_years/          # Year-level archive summary pages
├── _posts/               # Blog posts/news articles
├── _messages/            # Message pages from coaches/alumni
├── _plugins/             # Custom Jekyll plugins
├── assets/               # Static assets (CSS, JS, images)
├── game/                 # Game listing pages (index, all games, old-games)
├── team/                 # Static team pages
├── topics/               # Topics category pages
└── _tools/               # Custom Python tools for data processing
```

### Jekyll Collections

| Collection | Directory | URL pattern |
|---|---|---|
| games | `_games/` | `/game/:year/:name.html` |
| game_years | `_game_years/` | year archive pages via custom archives plugin |
| messages | `_messages/` | `/message/individual/:name.html` |
| posts | `_posts/` | `/topics/:year/:month-:day-:title.html` |

### Data Files (`_data/`)

- `member.csv` / `staff.csv`: Current roster and coaching staff
- `old-games.csv`: Historical game records
- `navigation.yml`, `next-games.yml`, `slide.yml`, `history.yml`, `faq.yml`: Navigation, schedule, and static content
- `featured-messages.yml`: Messages highlighted on the messages index page
- `topics-tags.yml`: Topic category definitions
- `link.yml`: External links (school, football organizations, university teams)

## Development

```sh
bundle install
bundle exec jekyll serve           # local dev
bundle exec jekyll serve --drafts  # include draft posts
```

Deployment is automatic on push to `main`: GitHub Pages (primary, serves nishi-owls.com) and Netlify (secondary, previews commits and branches including drafts/future posts).

### Content Files

- Game results: `_games/YYYY/YYYY-MM-DD-opponent.html`
- News articles: `_posts/YYYY/YYYY-MM-DD-title.md`
- When adding a new opponent or venue, update `_tools/known-names.yml` in the same commit

## CI/CD Validation (GitHub Actions)

Two workflows run automatically on PR and push to `main`:

**`validate-games.yml`** — triggered when `_games/**` files change
- Checks `result` (win/lose/tie) matches scores, required fields exist, and quarter sums add up

**`check-notation.yml`** — triggered when `_posts/**`, `_games/**`, or `_data/**` files change
- Checks notation consistency (表記ゆれ) and validates opponent/venue names

## Custom Tools (`_tools/`)

Install dependencies: `pip install -r _tools/requirements.txt`

- **`check-notation.py`**: Flags notation inconsistencies; rules in `notation-rules.yml`
- **`check-names.py`**: Validates `vs`, `vs_full`, filename slug, and `place` in game files against `known-names.yml`; also checks `next-games.yml`
- **`validate-game-results.py`**: Validates `result` field, required fields, and quarter score sums
- **`parse-results-table/main.py`**: Converts text-based possession tables to Markdown (`python3 _tools/parse-results-table/main.py < input.txt`)

## Custom Plugins (`_plugins/`)

**`file_date.rb`** — Liquid filter returning the Git commit date for a file (falls back to mtime):
```liquid
{{ "_data/member.csv" | file_date }}              {%- # → "YYYY年MM月" (default) -%}
{{ "_data/member.csv" | file_date: "%Y-%m-%d" }}  {%- # → "YYYY-MM-DD" -%}
```

**`archives/jekyll-archives.rb`** — Generates year-level game archive pages from `_game_years/`.

## Rules for AI Agents

- **After editing articles or game results**, always run the validation tools locally before finishing:
  ```sh
  python3 _tools/validate-game-results.py
  python3 _tools/check-notation.py
  python3 _tools/check-names.py
  ```
- **When renaming a page** that already exists on the `main` branch, add a `redirect_from` frontmatter entry so the old URL continues to work:
  ```yaml
  redirect_from:
    - /old/path/to/page.html
  ```

## Configuration Notes

- `site.featured_topic` in `_config.yml`: controls homepage featured announcement
- `_tools/` and `assets_data/` are excluded from the Jekyll build
- Timezone: Asia/Tokyo; language: `ja_JP`; strict Liquid filters enabled
