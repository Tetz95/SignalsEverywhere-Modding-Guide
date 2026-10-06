# 8. RailForge

RailForge loads Railloader-style mods, including SignalsEverywhere, and adds its own handling for signal mods. Most players use it, so test under it. It changes three things.

## It keeps untouched control points

Under RailForge, patching part of a module no longer deletes an interlocking, intermediate or crossover you didn't touch (see [What gets rebuilt](07-patching.md#what-gets-rebuilt)). Keep touching them anyway, so your mod works under plain Railloader too.

## It checks every patched module first

Before SignalsEverywhere builds anything, RailForge checks each module a mod patches. If a module fails a check, RailForge **defers** it: it removes your changes to that module, leaves the game's version running, and builds nothing new there. Other modules still apply. Nothing about this shows on screen, so a deferred module looks exactly like a patch that didn't work.

RailForge writes the reason to its support report, `Mods/RTM.RailForge/RailForge-support-report.txt`, under **`## Signal authoring`**. The section is rewritten every time a map loads and lists each deferred module with the path and the message. **When a module's changes are missing under RailForge, read that section first.**

The checks we've run into:

### Forward references

Everything a signal or predicate names must already exist **when that signal is created**: in the same module, in an earlier module, or in the game's own data. Modules are created in order, feature by feature, with the game's modules first and new modules after them in the order they appear in the patched data.

This bites predicate signals that name another control point. If module `AB-S` has a predicate signal naming interlocking `ab-w`, and `ab-w` is in module `AB-W` which comes later, RailForge defers `AB-S`. It also applies to the game's own modules: a stock predicate signal in `BR-E` that names `br-w` in `BR-W` (which comes after it) gets deferred as soon as your mod patches it.

Fixes:

- Put signals that name other control points in a module that comes after all of them. A new module is added after the existing ones, so a new last module works.
- For a stock predicate signal that has to keep its reference, `$moveTo` it into a later module and patch it there. The destination must already exist, so create it in one `signals` file and move into it from a second file.

Forward references to **blocks** are fine.

### Locations outside their segment

Every location you patch must lie within its segment as the track exists in the game right now. Other mods can change track: a mod that shortens a segment can make a stock signal's location invalid the moment you patch that signal, even if you didn't move it. If a module is deferred for a location you never changed, check whether another track mod moved or shortened that segment, and write the location from the other end or on the new segment.

### Removing predicate signals

RailForge refuses any patch that sets a predicate signal to `null`, because of the SignalsEverywhere crash (see [Known problems](07-patching.md#known-problems)), and defers the module. Tetz's SignalsEverywhere Fixes lets that one check through once the crash is fixed. Without it, don't remove predicate signals: move or rewrite them.

## Load order

RailForge orders mods by `loadAfter`. List every mod whose signals or panel you patch, and every mod that changes track your signals stand on, so your patches see their changes.
