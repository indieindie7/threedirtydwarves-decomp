# Three Dirty Dwarves (Sega Saturn + Windows, Appaloosa Interactive / SegaSoft, 1996) reverse-engineering notes and symbols

Hand-named function maps, review inputs and tools for **Three Dirty Dwarves**, a side-scrolling beat-em-up:
the Saturn release (T-30401H, SH-2) and the Windows release (DWARF.EXE, x86 PE, DirectDraw / DirectSound).
Round 1 (one naming pass over every function, then a review of every provisional name with its callers):

| Program | Functions | Hand-named | Still `provisional` |
|---|---|---|---|
| Saturn BOOT (0BOOT.DAT at 0x06010000) | 624 | 624 | 6 |
| Saturn overlays (LOGO.OVL, STAGE1..15.OVL at 0x06060000) | 104 | 104 | 1 |
| Windows DWARF.EXE | 1562 | 1326 (the other 236 are Ghidra import thunks and library names) | 30 |

Game: three dwarves, side-scrolling street brawls with thrown props (bins, crates, cabs) and a baseball bat;
the Saturn data files carry Hungarian names (ZSARU = cop, KUKA = bin, TAKU = cab, LADA = crate, KERIT = frame).
Subsystems named so far, Saturn: Sega GFS / CDC file system (`gfs_`, `cdc_`, `cd_`), VDP1 / VDP2 setup
(`vdp1_`, `vdp2_`, `dma_`), fixed-point and float helpers (`float_`, `math_`, `geom_`), the dwarf actors
(`dwarf_`, `obj_`, `anim_`, `hit_`), menus and text (`ui_`, `text_`, `font_`, `roster_`), overlay stage logic
(one small overlay per stage: spawners, boss timers, stage-specific props). Windows: the same game on
DirectDraw (`gfx_`, `drawq_`, `layer_`, `pal_`, `win_`), actors and props (`actor_`, `dwarf_`, `box_`, `debris_`),
cameras (`cam_`, `camera_`), per-stage logic (`stage9_`, `stage11_`, `stage13_`, `s5_`, `s14_`, `stgA_`: slice
prefixes that will be merged in round 2), sound (`snd_`), map and game state (`map_`, `game_`).

Same method as [rakugaki-decomp](https://github.com/indieindie7/rakugaki-decomp) and
[clockworkknight-decomp](https://github.com/indieindie7/clockworkknight-decomp): functions found by prologue
scan (Saturn) or Ghidra analysis (PC), a decompile dump cut into slices, each slice named from its code and
strings (prompts in `ghidra/naming/`), names applied as USER_DEFINED labels, then every provisional name
re-read with its callers by a local model (prompt in `ghidra/review/`, verdicts applied with `tools/srprovapply.py`).
Non-commercial, done for study and preservation (brawler design reference).

**No game data is included**: no disc image, no executables, no overlays, no decompiled C, no game text,
no Ghidra database. You need your own copy of the game to use any of this.

## What is here

| Path | Content |
|---|---|
| `NOTES.md` | disc and CD layout, load bases, Ghidra setup, the naming round, the review round, what comes next |
| `ghidra/hand_<prog>.txt` | hand names per program: `0x<addr> func <name> hand <comment>` (BOOT, DWARF, LOGO, STAGE1..15; apply with ApplyNames.java from the Scorcher / AMOK repos, hand mode) |
| `ghidra/funcinfo_<prog>.tsv` | per-function export: `F` address name source size, `C` callees (string rows removed) |
| `ghidra/naming/` | the round-1 naming prompts (BOOT, DWARF, overlays) |
| `ghidra/review/prompt_r1_tdd.txt` | the provisional-review prompt |
| `ghidra/scripts/` | `FindSh2FunctionsMem.java` (SH-2 prologue scan in a raw image), `CreateAt.java`, `CsDumpAll.java` (decompile dump with headers) |
| `tools/` | `basefind.py` + `basechk.py` (load-base histograms for raw Saturn images), `decprep.py` (slice a dump), `decmerge.py` (merge slice names), `ckprovctx.py` (review contexts with callers), `srprovapply.py` (apply review verdicts), `pubfuncinfo.py` |

## Licence

Notes, names and tools: MIT (see `LICENSE`). Three Dirty Dwarves belongs to its rights holders; nothing from the
game is distributed here.
