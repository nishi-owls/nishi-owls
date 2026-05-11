# Overview

Official website for Tokyo Metropolitan Nishi High School American Football Team "OWLS" (都立西高アメリカンフットボール部 OWLS).

**URL**: https://www.nishi-owls.com — GitHub Pages (primary) / Netlify (secondary, preview)

# Structure

Standard Jekyll directories (`_layouts/`, `_includes/`, `_sass/`, `assets/`) plus:

- `game/`, `team/`, `topics/` — static page directories (not Jekyll collections)
- `_data/` — YAML/CSV data files; see Data Files below
- `_games/`, `_game_years/`, `_posts/`, `_messages/` — Jekyll collections; see Collections below
- `_plugins/` — custom Jekyll plugins; see Plugins below
- `_tools/` — Python data tools; see Tools below
- `assets_data/` — original-size images and unused candidate photos (record only, excluded from build)

## Collections

| Collection | Directory | URL pattern |
|---|---|---|
| games | `_games/` | `/game/:year/:name.html` |
| game_years | `_game_years/` | `/game/:year/` |
| messages | `_messages/` | `/message/individual/:name.html` |
| posts | `_posts/` | `/topics/:year/:month-:day-:title.html` |

## Data Files

- `member.csv` / `staff.csv`: Current roster and coaching staff
- `old-games.csv`: Historical game records
- `navigation.yml`, `next-games.yml`, `slide.yml`, `history.yml`, `faq.yml`: Navigation, schedule, and static content
- `featured-messages.yml`: Messages highlighted on the messages index page
- `topics-tags.yml`: Topic category definitions
- `link.yml`: External links (school, football organizations, university teams)

# Development

```sh
bundle install
bundle exec jekyll serve           # local dev
bundle exec jekyll serve --drafts  # include draft posts
```

Deployment is automatic on push to `main`: GitHub Pages (primary, serves nishi-owls.com) and Netlify (secondary, previews commits and branches including drafts/future posts).

# CI/CD

Two workflows run automatically on PR and push to `main`:

**`validate-games.yml`** — triggered when `_games/**` files change
- Checks `result` (win/lose/tie) matches scores, required fields exist, and quarter sums add up

**`check-notation.yml`** — triggered when `_posts/**`, `_games/**`, or `_data/**` files change
- Checks notation consistency (表記ゆれ) and validates opponent/venue names

# Tools

Install dependencies: `pip install -r _tools/requirements.txt`

- **`check-notation.py`**: Flags notation inconsistencies; rules in `notation-rules.yml`
- **`check-names.py`**: Validates `vs`, `vs_full`, filename slug, and `place` in game files against `known-names.yml`; also checks `next-games.yml`
- **`validate-game-results.py`**: Validates `result` field, required fields, and quarter score sums
- **`parse-results-table/main.py`**: Converts text-based possession tables to Markdown (`python3 _tools/parse-results-table/main.py < input.txt`)

# Plugins

**`file_date.rb`** — Liquid filter returning the Git commit date for a file (falls back to mtime):
```liquid
{{ "_data/member.csv" | file_date }}              {%- # → "YYYY年MM月" (default) -%}
{{ "_data/member.csv" | file_date: "%Y-%m-%d" }}  {%- # → "YYYY-MM-DD" -%}
```

**`archives/jekyll-archives.rb`** — Generates year-level game archive pages from `_game_years/`.

# Workflows

## Adding a game result

### Phase 1: 速報・写真 (publish on game day)

Human inputs: scores, quarter breakdown, possession table, brief draft notes, photos (resized and originals).

1. Create `_games/YYYY/YYYY-MM-DD-opponent.html`:
   - Frontmatter: `date`, `season`, `game_name`, `place`, `start_at`, `vs`, `vs_full`,
     `our_scores` (array per quarter), `our_score`, `vs_scores`, `vs_score`, `result`,
     `social_image: "/assets/images/topics/YYYY/MM-DD-opponent-1.jpg"`
   - Possession table (`{: .possessions}`)
   - Link line: `[写真と試合結果の記事はこちら](/topics/YYYY/MM-DD-opponent.html)`
2. Create `_posts/YYYY/YYYY-MM-DD-opponent.md`:
   - Frontmatter: `tags: news`, `title`, `image: YYYY/MM-DD-opponent-thumb.jpg`,
     `social_image: "/assets/images/topics/YYYY/MM-DD-opponent-1.jpg"`
   - Body: A summary based on the human draft and game data
   - Embed photos:
     ```markdown
     ![試合風景写真](/assets/images/topics/YYYY/MM-DD-opponent-N.jpg)
     {: .image-box .center}
     ```
   - Include a `## 次の試合について` section with links to recent past games vs. the next opponent
3. Place resized photos at `assets/images/topics/YYYY/MM-DD-opponent-N.jpg` and thumbnail at `…-thumb.jpg`; place originals at `assets_data/topics/YYYY/`
4. Update `_data/next-games.yml` to the next scheduled game
5. If the opponent or venue is new, add it to `_tools/known-names.yml`
6. Run validation tools (see Rules below) and commit all files together

### Phase 2: 詳細ゲームレポート (a few days later)

Human inputs: detailed play-by-play report text.

1. Add to the game file after the possession table:
   ```html
   <!-- prettier-ignore -->
   <h2>ゲームレポート</h2>
   <div class="game-report-detail">
   <!-- detailed content here -->
   </div>
   <!-- prettier-ignore -->
   ```
2. Run validation tools and commit

# Rules

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

# Configuration

- `site.featured_topic` in `_config.yml`: controls homepage featured announcement
- Timezone: Asia/Tokyo; strict Liquid filters enabled
