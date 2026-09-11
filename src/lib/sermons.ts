import raw from '../../data/sermons.json';

export interface PdfGuide {
  label: string;
  source_url: string;
  local_path: string | null;
}

export interface Sermon {
  id: number;
  slug: string;
  title: string;
  date: string;
  link: string;
  excerpt: string;
  categories: string[];
  tags: string[];
  transcript: string;
  youtube_id: string | null;
  pdf_guides: PdfGuide[];
  thumbnail: string | null;
  _scrape_ok: boolean;
}

const LANG_ORDER = ['English', 'Spanish', 'Portuguese', 'Filipino', 'Swahili'];

function guessLanguage(guide: PdfGuide): string {
  const source = `${guide.local_path ?? ''} ${guide.source_url}`;
  for (const lang of LANG_ORDER) {
    if (source.includes(lang)) return lang;
  }
  return guide.label || 'Sermon Guide';
}

export function getSermons(): Sermon[] {
  const list = (raw as Sermon[]).filter((s) => s._scrape_ok);
  return list
    .map((s) => ({
      ...s,
      pdf_guides: s.pdf_guides.map((g) => ({ ...g, label: guessLanguage(g) })),
    }))
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

export function getSermonBySlug(slug: string): Sermon | undefined {
  return getSermons().find((s) => s.slug === slug);
}

export function getAllSeries(): string[] {
  const set = new Set<string>();
  for (const s of getSermons()) {
    for (const c of s.categories) set.add(c);
  }
  return Array.from(set).sort();
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: '2-digit' });
}

export function scriptureFromTitle(title: string): string | null {
  const m = title.match(/([1-3]?\s?[A-Za-z]+\.?\s\d+[:.]\d+(?:-\d+)?)/);
  return m ? m[1] : null;
}
