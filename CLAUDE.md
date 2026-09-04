# Working in this repository

A physical knob that sits on the nightstand and controls the house: lights,
music, scenes. The second knob — the first one grinds coffee
(`tomereli/coffee-knob`), and what was learned there applies here.

## Move fast and break things. Just not all things.

The motto, and a working instruction rather than a slogan. Tomer is the
only user of everything here, so the cost of a thing breaking is close to
zero. Build it now: the setup cost never gets cheaper, and retrofitting is
what actually costs. Pricing hypothetical operational burden as if this
were a production service with customers is the failure mode to avoid.

The not-all-things list for this project: anything that can leave the
bedroom dark or the house unlocked, and the Home Assistant configuration
other automations depend on. Everything else is fair game to try, ship,
and fix in flight.

**The AC and FAN cards are finished.** They read correctly under the hand
in the dark and they are not to be redesigned — not their layout, not
their rings, not their type. A change elsewhere may touch them only where
it must to keep compiling. Anything that would alter how either card looks
or behaves needs Tomer to ask for it first, by name.

## This repo is built by the AISDLC pipeline

Work does not get written by hand here. It arrives as an issue and leaves
as a deploy:

1. Talk the idea through with Tomer until it is concrete.
2. File a GitHub issue in the contract shape — problem, acceptance
   criteria as `WHEN X THE SYSTEM SHALL Y` clauses, affected surfaces,
   out of scope. The template is `enroll/issue-contract.md` in
   `tomereli/aisdlc`.
3. Label it `sdlc:ready` plus a `size:S|M|L`. Add `needs:ux` for anything
   a person looks at or touches — a knob's behaviour under the hand counts
   as UX, and the crew will stop for a design review before building.
4. A dispatcher on Tomer's PC picks it up within a minute and runs a crew:
   architect, designer where relevant, developers, QA, reviewer, gates,
   merge, release.

You do not need to run anything for this to happen, and you should not
implement the issue yourself. Filing a good issue is the work.

## Physical things are not web things

This is hardware with firmware, so two habits from the software repos do
not transfer:

- **A wrong turn of a knob is felt immediately.** There is no "it renders
  fine" — latency, detents and haptics are the product. Whatever gets
  built must be tried by hand before it counts as done.
- **Bricking is real.** Anything touching the bootloader, the flashing
  path, or the pairing state belongs to the not-all-things list, and gets
  the same treatment as a database migration: back out a way first.

## Where the rest of the context lives

`tomereli/aisdlc` — the pipeline, its roles, and how the gates work.
`tomereli/coffee-knob` — the previous device, including what its
integration with Home Assistant already solved.
