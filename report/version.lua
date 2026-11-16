-- Adds the version the report is built from, `git describe` of the checkout, to the title page's date line.
local ok, out = pcall(pandoc.pipe, 'git', {'describe', '--tags', '--always', '--dirty'}, '')
local version = ok and out:gsub('%s+$', '') or 'unknown (built outside a git checkout)'

function Meta(meta)
  meta.date = pandoc.Inlines(meta.date or {}) .. {pandoc.LineBreak(), pandoc.Str('Version ' .. version)}
  return meta
end
