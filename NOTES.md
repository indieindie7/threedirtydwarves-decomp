# Three Dirty Dwarves decomp notes (names + notes only; no game data)

## Saturn disc (2026-10-17)
- US release T-30401H V1.011, own copy, 9 tracks (track 1 data, 2-9 CDDA). Extracted with a 2352-byte-sector ISO reader: 259 files.
- IP header: first read address 0x06010000, size 0x10000. Boot program = 0BOOT.DAT (243,464 bytes).
- Root files: TDDLO.BIN (872,800, a table of 0x20-byte entries, data), KERIT.BIN (172,672, UI frame data; Hungarian keret = frame), DUKSEGA.BIN (logo), KERIT.PAL. Folders INTRO, LOGO, MAP, SECRET, STAGE1..STAGE15: A_*.BIN = actor sprite sets (BIGORC, PUNK, ZSARU = cop, KUKA = bin, ORC, TAKU = cab, LADA = crate), B_* = background props (TUSKE = spike, LAMPA = lamp, BUMM = explosion, RUD = rod).
- Load bases (`tools/basefind.py` + `tools/basechk.py`, big-endian pointer histograms): 0BOOT.DAT at 0x06010000 (577 pointer entries, 1,597 hits). TDDLO.BIN and KERIT.BIN are data, not code (fewer than 12 prologue hits at any base). Each STAGE<n>/STAGE<n>.OVL and LOGO/LOGO.OVL (9-48 KB, 16 files) loads at 0x06060000.

## Windows release (2026-10-17)
- InstallShield 3 CD: DWPLAY.EXE launcher, DATA.Z holds the game (PKWARE DCL implode archive). The game exe DWARF.EXE: PE, MSVC linker 3.10, link time 1996-12, .text 680,960 bytes, imports ddraw / dsound / DISPDIB / LZ32 / winmm.
- A community speed-fix build adds a 167-byte section that imports an fps.dll; the function map here is for the game code, which is identical in both.
- PC data: TDDLOW.PWD/PWH, A_*.PWD/PWH sprite packs, STAGE<n>/B_MAP<nn>.PLH/PLN.

## Ghidra (12.1.4)
- Saturn: BinaryLoader, SuperH:BE:32:SH2, BOOT at 0x06010000, overlays at 0x06060000; `FindSh2FunctionsMem.java` prologue scan + `CreateAt.java`: BOOT 624 functions; overlays LOGO 11, STAGE1 4, STAGE2 4, STAGE3 4, STAGE4 4, STAGE5 3, STAGE6 9, STAGE7 10, STAGE8 5, STAGE9 3, STAGE10 7, STAGE11 7, STAGE12 20, STAGE13 3, STAGE14 7, STAGE15 3 (104). The overlays make no direct calls into BOOT; they are reached through tables.
- PC: PE loader, x86 default cspec, full analysis: 1,562 functions (236 of them Ghidra import thunks / library names), 491 strings. The MinGW pseudo-reloc analyzer error is harmless.
- `CsDumpAll.java` writes the decompile dump per program.

## Naming round 1 (2026-10-17)
- `decprep.py` cuts each dump into slices (BOOT 5, DWARF 9, one per overlay); one naming agent per slice with the prompts in `ghidra/naming/` (every name comes from reading the code and strings, never from a script); `decmerge.py` merges the slices.
- ApplyNames (hand mode) + export: BOOT 624/624 named (137 provisional), DWARF 1,326/1,326 (492 provisional), overlays 104/104 (6 provisional: STAGE8 1, STAGE10 2, STAGE12 3). 0 FUN_ anywhere.

## Review round 1 (2026-10-17 .. 10-18)
- `tools/ckprovctx.py` writes one context per provisional function (its decompile plus up to three callers); a local model answers one verdict line each with `ghidra/review/prompt_r1_tdd.txt`: `<PROG> 0x<addr> <old> CONFIRM|RENAME|UNSURE <new> <reason>`.
- `tools/srprovapply.py` applies the verdicts: BOOT confirmed 104, renamed 27, unsure 6; DWARF confirmed 377, renamed 85, unsure 30; overlays confirmed 5, unsure 1 (STAGE12). Re-applied and re-exported: BOOT 6 provisional, DWARF 30, overlays 1, 0 FUN_.
- The review ran twice: the first run died on a busy GPU (the model needs about 11 GB of VRAM) and resumed from its JSONL log.

## Next
- Round 2: merge the DWARF slice prefixes (`s5_`, `s14_`, `stgA_`, `stage9_` / `stage11_` / `stage13_` into one `stage<n>_` scheme), re-read the 37 remaining provisional names, and align BOOT against DWARF by string (the PC build keeps the strings the Saturn build drops).
- The Saturn overlay call tables (how BOOT reaches the per-stage overlay entry points) are not mapped yet.
