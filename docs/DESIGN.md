# Pathshala study workspace — version 2

The product is a bilingual reading companion for four Bengali textbooks. Its distinctive interaction is opening the exact source next to an answer. The design should feel like an attentive reading room, with enough visual identity to make the four books easy to recognize.

Palette: canvas #F6F8FB, paper #FFFFFF, ink #192B43, secondary #64738B, primary #355EDD, divider #E4E9F1. Book colors: muted cobalt, sea green, plum, and ochre. Use book-cover typography and simple geometric botanical motifs rather than fake thumbnails or generic feature icons.

Type: Manrope for navigation and Latin text; Noto Sans Bengali for Bengali text. Left aligned reading text, 18px Bengali body, 1.75 line-height. The Bengali welcome heading and cover titles create identity; avoid decorative gradients and high-contrast marketing copy.

Layout: 240px sidebar with library and recent sessions; main area capped at 1000px. Four compact book choices lead into a spacious question composer and topic prompts. On a conversation, the welcome content yields to messages. Citations open a right-side evidence reader, collapsing to a modal on mobile.

States: home, topic lesson, library, selected book, loading, indexing/not ready, answered, unsupported, board-question list, attempt editor, hints, rubric feedback, easy solution, notebook, audio player, video player, media queue, provider failure, settings, and source reader. Every control must have a real operation. No invented learning streaks, fake user profiles, or simulated scores.

Preflight review: a normal card grid would hide the key interaction. Use book spines/covers only in the library, and ordinary flowing prose for answers. Keep all four books visible without making the page look like a course marketplace. Information about source availability belongs next to the selected book; API/model diagnostics belong in settings.

The expanded navigation is Home, Learn, Practice, Notebook and Progress. Topic pages use flowing reading layouts. Practice uses a focused question-and-answer workspace. Audio and video belong to the lesson rather than a separate media feed. Show source tier with text: Textbook, Board, Official key, Guide, or Pathshala explanation. Low-bandwidth mode prioritizes text and audio and never auto-loads video.
