-- Adds the version the report is built from, `git describe` of the checkout, and the repository's address to the title page's date line.
local repository = 'https://github.com/Alef-Keuffer/feup.devops.places'

local ok, out = pcall(pandoc.pipe, 'git', {'describe', '--tags', '--always', '--dirty'}, '')
local version = ok and out:gsub('%s+$', '') or 'unknown (built outside a git checkout)'

-- The version links to its tag only when it is a bare tag; `<tag>-N-g<hash>` and `<tag>-dirty` name no tag.
local tag_ok, tag = pcall(pandoc.pipe, 'git', {'tag', '--list', version}, '')
local on_tag = tag_ok and tag:gsub('%s+$', '') == version

function Meta(meta)
  local shown = on_tag and pandoc.Link(version, repository .. '/tree/' .. version) or pandoc.Str(version)
  meta.date = pandoc.Inlines(meta.date or {}) .. {
    pandoc.LineBreak(), pandoc.Str('Version '), shown,
    pandoc.LineBreak(), pandoc.Link(repository, repository),
  }
  return meta
end
