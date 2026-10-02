# Pathshala UI/UX Specification

**Version:** 2.0

**Product direction:** A calm bilingual reading room centered on trustworthy source inspection
**Related documents:** [Application flow](APP-FLOW.md), [TRD](TRD.md), [Design seed](DESIGN.md)

## 1. Experience objective

Pathshala should feel like opening a well-kept desk with the right book already beside the student. It is neither a generic chatbot nor a course marketplace. The product’s recognizable interaction is the answer-source relationship: every supported answer can open the original Bengali passage next to it.

The interface should reduce the hesitation students feel when they do not know how to phrase a question. It should also make uncertainty visible without sounding mechanical. Technical implementation terms belong in preferences and diagnostic views, not the study flow.

## 2. Audience and use context

Primary users are SSC and HSC students in Bangladesh using phones, shared computers, and ordinary laptop screens. They may switch between Bengali and English, use mixed-script queries, and have inconsistent connectivity. Bengali reading quality matters more than dense information display. Sessions are short and question-driven, while saved answers support later revision.

The UI must work for:

- a first-time student who needs an example question;
- a student who knows the exact passage or grammar rule;
- a student who asks an English question about Bengali evidence;
- a keyboard or screen-reader user;
- a student returning to a recent or saved explanation;
- a student whose selected book is not ready or lacks the answer.

## 3. Information architecture

```text
Pathshala
├── Study companion
│   ├── Welcome and book selection
│   ├── Conversation
│   └── Evidence reader
├── My library
│   ├── All books
│   ├── SSC
│   ├── HSC
│   └── Book details
├── Saved answers
├── Recent conversations
├── How Pathshala works
└── Preferences
```

The desktop sidebar owns navigation and recent conversations. The mobile sidebar becomes a drawer. The top bar names the current destination and exposes a source-trust explanation. The central workspace changes among Welcome, Conversation, Library, and Saved Answers.

## 4. Visual direction

### 4.1 Concept

The interface uses the restraint of a reading room with four recognizable book objects. Covers use muted academic colors and line-drawn botanical or typographic motifs. The covers help selection; answers remain flowing text rather than nested cards.

The strongest visual moment is opening the evidence reader beside an answer. The source excerpt receives a quiet vertical rule, generous Bengali line height, and direct access to the PDF page. Decorative effects must not compete with the text.

### 4.2 Color system

| Token | Value | Usage |
|---|---|---|
| Canvas | `#F6F8FB` | Main background |
| Paper | `#FFFFFF` | Sidebar, composer, dialogs, evidence panel |
| Ink | `#192B43` | Primary headings and controls |
| Body | `#52637A` | Long-form answer text |
| Muted | `#758298` | Metadata and secondary navigation |
| Line | `#E4E9F1` | Dividers and control borders |
| Action | `#355EDD` | Primary buttons, selected states, links |
| Success | `#6DA896` | Ready and verified status |
| Warning | `#C9AC73` | Preparing or review-required status |
| Error surface | `#FFF2EC` | Recoverable error banner |
| Error text | `#A66A4C` | Error explanation and actions |

Book identities use muted cobalt for SSC First, sea green for SSC Second, plum for HSC First, and ochre for HSC Second. These colors aid recognition but never carry the only indication of level or paper.

All actual combinations must meet WCAG 2.2 AA contrast. Muted text below the minimum contrast must be revised during browser testing rather than retained for visual softness.

### 4.3 Typography

- Bengali: Noto Sans Bengali, 400–600.
- Latin and UI labels: Manrope, 400–800.
- Bengali answer text: 17–18 CSS pixels, line height 1.85–2.0.
- Latin body text: 14–16 pixels, line height 1.6–1.75.
- Reading width: ideally 60–75 Latin characters or an equivalent comfortable Bengali measure.
- Bengali text must not use tracking or forced uppercase transformations.
- Headings use sentence case. All-caps is limited to the small brand wordmark where it carries a real identity role.

## 5. Layout system

### Desktop, 1200 pixels and above

```text
┌────────────────────┬───────────────────────────────────┬────────────────────┐
│ Brand              │ Destination / context             │ Source trust       │
│ New conversation   ├───────────────────────────────────┤                    │
│ Main navigation    │ Selected book                     │ Evidence header    │
│ Recent sessions    │                                   │                    │
│                    │ Question                          │ Original excerpt   │
│                    │ Answer and citations              │                    │
│ Help               │                                   │ Open original PDF  │
│ Preferences        │ Composer                          │                    │
└────────────────────┴───────────────────────────────────┴────────────────────┘
      240 px                    fluid, max 950 px              350 px on demand
```

The evidence panel appears only when requested. The central reading column shrinks without letting answer text become uncomfortably narrow. At intermediate laptop widths, the evidence panel overlays the right side instead of permanently compressing the study column.

### Tablet, 681–900 pixels

The sidebar may stay visible if space permits, but the welcome book picker uses two columns and prompt suggestions use one column. Evidence opens as an overlay. The top bar removes nonessential source-trust copy.

### Mobile, 320–680 pixels

The sidebar becomes a drawer opened by a labeled menu button. The study workspace is one column. The four-book picker uses two compact items; the library uses two covers when width permits and one when 200% zoom forces it. Evidence becomes a full-screen sheet. The composer remains reachable but must not cover the active answer when the on-screen keyboard opens.

## 6. Core screen specifications

### 6.1 Study welcome

Purpose: help the student choose a book and ask without requiring onboarding.

Required elements:

- Bengali welcome heading and short bilingual-support description;
- “Start with your textbook” book picker containing exactly four choices;
- selected-book state using border, check mark, and text;
- large question composer with real answer-language control;
- three suggestions tailored to first-paper literature or second-paper grammar;
- explanation of source-grounded answers;
- source readiness status.

Selecting a suggested question populates and focuses the composer; it does not submit immediately. Selecting a book resets the unsent conversation scope and updates suggestions.

### 6.2 Conversation

Questions and answers use a readable vertical flow. Student questions have a compact neutral avatar. Pathshala answers use the book mark and a status label. The assistant answer uses Markdown rendered without raw HTML.

Answer actions appear after content:

- Copy copies answer text only.
- Save toggles the persisted saved state.
- Helpful records a positive rating.
- Incorrect records or opens negative feedback.
- Citations open source evidence.

While generating, the student question remains visible and a live status says the system is reading and locating passages. Avoid fake progress percentages and animated word-by-word filler.

### 6.3 Library

The library presents four book covers with SSC/HSC filter tabs and title search. Each book exposes paper, short description, readiness, page count, passage count, and Study this book. Book details explain source provenance and syllabus limitations.

The page should resemble a small personal shelf. It must not introduce pricing, ratings, completion percentages, invented authors, or course badges.

### 6.4 Saved answers

The empty state explains why saving is useful and returns the student to the composer. Populated results preserve question, answer, source citations, book, and original session relationship. An answer whose session expired must show a source-unavailable state rather than a broken citation button.

### 6.5 Evidence reader

Required content:

- selected book and level;
- PDF page number and optional printed page when available;
- canonical original excerpt in Bengali;
- button to open the session-pinned PDF;
- concise pagination disclaimer;
- close control with focus restoration.

The quoted fragment used by the answer can be highlighted after the basic panel is correct. Highlight matching must tolerate whitespace normalization without changing the displayed source.

### 6.6 Preferences

Expose answer language, privacy disclosure, retention, and safe service details. It may name model identifiers and whether retrieval/reranking is enabled. It must not show API keys, host filesystem paths, internal prompts, raw provider errors, or full traces.

## 7. Component inventory

| Component | States | Key behavior |
|---|---|---|
| Book cover | default, selected, unavailable | Distinguishes book; accessible name is supplied by parent control |
| Book picker item | idle, hover, focus, selected, disabled | Sets new-conversation collection |
| Composer | empty, typing, disabled, error | Preserves text on failure; Enter sends, Shift+Enter adds line |
| Language selector | auto, Bengali, English | Applies to subsequent answer |
| Send button | disabled, ready, pending | Prevents local duplicates |
| Answer | answered, clarification, unsupported | Shows only actions valid for stored outcomes |
| Citation chip | idle, loading, open, failure | Opens owned evidence and restores focus |
| Evidence panel | loading, content, error | Overlay behavior under 1150 pixels |
| Recent item | idle, selected, deleting | Opens or deletes owned session |
| Status indicator | ready, preparing, review, unavailable | Includes text in addition to color |
| Toast | success, informational | Announces outcome; does not contain critical-only information |
| Dialog | help, book details, preferences | Traps focus and closes with Escape |

## 8. Content design

Use plain language centered on the student’s task. Preferred patterns:

| Situation | Recommended copy |
|---|---|
| Book ready | “265 pages ready to study” |
| Book preparing | “This textbook is still being prepared.” |
| Unsupported | “I couldn’t find enough support for that answer in this book.” |
| Ambiguous | “Which character or passage do you mean?” |
| Provider timeout | “The answer service took too long. Your question is still here.” |
| Session expired | “This temporary conversation has expired. Start a new one with the same book.” |
| Citation action | “Open source” or “PDF page 42” |

Do not tell students that the system is “thinking,” “confident,” or “100% accurate.” Do not call a provider outage a missing textbook answer. Avoid vague errors such as “Something went wrong” when the application knows the recovery step.

## 9. Accessibility behavior

- Use `aside`, `nav`, `main`, `header`, `article`, and `dialog` landmarks appropriately.
- Every icon-only control requires an accessible name.
- The active navigation destination uses both visual treatment and `aria-current` in the implementation.
- Book-selection controls expose `aria-pressed` or radio semantics.
- Pending-answer changes use a polite live region. Errors use an assertive alert only when immediate action is required.
- Opening a dialog or evidence sheet moves focus inside; closing restores it to the trigger.
- Keyboard order follows visual order. No action is hover-only.
- Touch targets are at least 44×44 pixels for primary mobile controls.
- At 200% zoom, content reflows without horizontal page scrolling.
- Reduced-motion users receive no animated scrolling or continuous spinner dependency; loading text remains sufficient.
- Bengali strings are tested on Safari, Chrome, and Android Chrome for clipped marks and fallback-font changes.

## 10. Interaction and motion

Motion explains state changes. Use a short 160–220 ms panel or drawer transition, subtle button state changes, and one initial content reveal at most. Do not animate every card or answer. Respect `prefers-reduced-motion` and keep the content fully understandable without animation.

The composer should remain stable when error text appears. Loading and retry must not move the send button unexpectedly. Auto-scroll only when the user is already near the newest message; otherwise show a “New answer” control.

## 11. Design tokens

The implementation should migrate repeated values into CSS custom properties:

```css
:root {
  --color-canvas: #f6f8fb;
  --color-paper: #ffffff;
  --color-ink: #192b43;
  --color-body: #52637a;
  --color-muted: #758298;
  --color-line: #e4e9f1;
  --color-action: #355edd;
  --radius-control: 8px;
  --radius-panel: 12px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
}
```

Use radius by function: tighter for controls, wider for composer and dialogs, minimal for book covers. Shadows should indicate elevation for dialogs, drawers, and physical book covers only.

## 12. UX acceptance checks

1. A new student can select a book and send a question without instructions.
2. A Bengali answer at 200% zoom has no clipped glyphs or horizontal page scroll.
3. A keyboard user can choose a book, send, open evidence, close it, and return to the citation.
4. A screen reader announces loading, answer completion, and errors without duplicate chatter.
5. A failed answer preserves the exact question and offers the right recovery action.
6. A citation cannot display evidence from another book or version.
7. Mobile navigation, dialog, and evidence overlays trap and restore focus correctly.
8. Every visible control performs a real operation or is removed before release.

## 15. Version 2 information architecture

```text
Pathshala
├── Home
├── Learn
│   ├── Course / paper
│   ├── Chapter and topic
│   ├── Text lesson
│   ├── Ask
│   ├── Listen
│   └── Watch
├── Practice
│   ├── Board-question explorer
│   ├── Attempt workspace
│   ├── Hints
│   └── Solution and rubric
├── Notebook
│   ├── Saved explanations
│   ├── Notes
│   ├── Flashcards
│   └── Weak topics
└── Progress
```

Desktop uses a stable left rail for these five destinations. Mobile uses a five-item bottom navigation with the current task preserved. The selected level and paper remain visible as a compact context switcher.

## 16. Topic page

The topic page leads with a readable explanation and a slim source rail. “Ask about this,” “Try questions,” “Listen,” and “Watch” are direct actions beneath the title. A sticky table of contents appears only for long lessons. Source tier badges use text and icons in addition to color: Textbook, Board, Official key, Guide, Pathshala explanation.

Avoid turning the page into a dashboard of cards. Use continuous lesson typography, margin notes, diagrams where they explain a concept, and a compact related-question strip after each section.

## 17. Practice workspace

Desktop layout: question/rubric context on the left and the answer editor on the right. Mobile: question, editor, and feedback appear in order. The solution remains collapsed until submission or an explicit “Show solution” action. Hint buttons describe their cost to the attempt state. Timers are optional and never use urgency animations.

Feedback separates:

- “You included” with matched rubric points;
- “Add or improve” with missing points;
- “Check the book” with citations;
- “See an easy answer” with expandable steps;
- “Try again” with the answer retained in revision history.

## 18. Audio/video experience

Audio is an inline player attached to a lesson version. It exposes transcript, 0.75×–2× speed, 10-second skip, chapter markers and background playback where supported. Bengali transcript highlighting must not reduce screen-reader access.

Video is a 16:9 captioned lesson player with chapter navigation below it. Captions start on, source citations are available without pausing, and an audio-only mode reduces bandwidth. Loading states distinguish queued, scripting, narrating, rendering and ready, without fake percentages. Students can leave the page and receive an in-app ready state later.

## 19. Student-friendly language

Use short Bengali labels and explain academic actions through outcomes. Prefer “ইঙ্গিত দেখো” (see a hint), “সহজ সমাধান” (easy solution), “বইয়ে দেখো” (see in book), and “আবার চেষ্টা করো” (try again). Do not say vector, chunk, reranker, inference, or confidence score in student views.

## 20. New accessibility checks

1. Practice editor, hints and rubric work without pointer input.
2. Audio controls have names, time values and keyboard operation.
3. Every video has synchronized captions and a complete transcript.
4. Meaningful diagrams have Bengali descriptions; decorative frames are hidden.
5. Tier and review state never rely on color alone.
6. Low-bandwidth mode avoids auto-loading video and offers audio/text first.
