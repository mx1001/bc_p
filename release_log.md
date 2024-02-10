### 7.1.V
Major

- Re - Origin
	○ Cutter Origin Options
		§ Mouse Position - mouse start position
		§ Initial Center - center before extrusion. Surface origin
		§ Bounding box Center - center as core of shape
		§ Active Object center - center as object used for cut
	○ Added to D Pie / N panel

- Transformation Re-entry
	○ G- Grab
		§ Transformation Global X / Y / Z
		§ Transformation Local w/ rotation
		§ Shift + Grab offset dot to translate
	○ R - Rotation
		§ Rotate with R
		§ Change axis with X / Y / Z
			§ Uses same axis on next draw
			§ Axial change in Shape Panel of behavior
		§ Snap automatically set to 5
			§ Snap panel locations
				□ Ctrl + D Helper
				□ Snap Options

- Alt + D Toggle Dots
	○ Display dots added to Display dropdown

- Viewport Hotkey in pause unlock
	○ 1/3/7 capable of view change
- Viewport ~ pie unlock toggle
	○ Sets shift + ~ to rotate shape

- Release lock toggle for touchscreeen
	○ Draws unto a tabbed state.
	○ Quick Execute unto auto lazorcut
		§ Compatible w/ accucut resulting in a nicer fit.
			§ Compatible w/ accucut depth
			§ Compatible without accucut
		§ Offset draw w/ offset results in perfect fit on LMB
		§ Ngon fixed


- Slice Adjustment (smart apply level)
*show w/ slicing then moving freely since unapplied*

- Recut

- Knife cut material cut issue resolved
- Knife mark hops link
	○ Shift + K
- Release Lock + Quick Execute = Godray
- Autohide to hide solid

Minor
- Inherent fix for emulate numpad
	○ Extending to:
		§ Solidify
		§ Mirror
- Hook support
- Apply Scale Improvements and toggle
	○ Improving
		§ Lazorcut
		§ Bevel
- Array
	○ Shape Panel of behavior
		§ Start Options

- Weld w/ small scale improvements

- Shift to live select Inset on inset
	○ Bevel bypass w/ Inset Improvements
	○ Modifiers no longer removed w/ inset

- Weighted Normal Inset Removal
	○ Custom cutter normal data removal
- Bevel flip fix
- Delete shape make bug fixed
- View Aligned Error Prevention
- D pie improvements
	○ Origin options
	○ Shape draw origin options
- Ngon backspace fix
	○ Ctrl + Z during ngon will undo without breaking out of draw

Mirror fix

## 715

715
	- Grid
	- Sort V3
	- Quick Execute Improvements
		○ Depth connection
	- Delete Cutters
	- Lazorcut Depth

715.5
	- Alt + W topbar toggle
	- Circle Oval Bugfix
	- Local mode blue box
	- Getting rid of Q dot in tab


	- Matcut
		○ Inset special behavior
	- Weld Sort
	- Xray to solid during draw
	- L to live Ver2
	- 2d Box Weld Support
	- Shift to live / active fix
	- Grey grid on deselect
	- Mirror Dimension Smart draw
	- Weld mod support to bevel / ngon 282

	- Inherent fix for emulate numpad
		○ Extending to:
			§ Solidify
			§ Mirror
	- Hook support
	- Apply Scale Improvements and toggle
		○ Improving
			§ Lazorcut
Bevel

## 714

	- Fade
		○ Fade Options
	- Extraction Hide
	- Accucut
	- Edit Mode Dots
	- Radial Array
	- Knife Box Wire Display
Sound FX

## 713

- Extraction
- Fade Distance Improvements (distance accuracy)
- Ngon Cyclic
- Extraction To Box
- Circle Decimate Fix (128 support)
- Decimate Sort Support
- Behavior Adjustment (wat)
- Knife Project Classic
- R to reset / rotate Array
- R for initial rotate
- Bevel to Chamfer and back
- Custom Shape Knife Project Support (grid cut)
- Slim Topbar Alt
- Remesh Sort Support
HOPS support back bevel

## 712

Boxcutter 712
	- Shape Recollection
	- Logo Cutter
	- Self Cutter
	- Custom Cutter
	- ~ to rotate custom shape 90 degree during draw
	- Snapping Dots
		○ Unit (supports Imperial And Metric)
		○ Viewport dots
		○ Face / Vert / Edge Mid
		○ Active Only Dots
		○ World Dots
		○ Faded / Distance Based
	- Custom Initial Hotkey
	- Boolean Autohide Fix
	- Alt / Shift Draw Modifier
	- Corner Box Draw
	- Ngon Point Undo
	- Mod Sort Level 2
	- Latest Bevel Sorting
	- Triangulate Mod Sorting
	- Solidify Limit Fix
	- Performance Improvements
	- Cutter Uvs

	712.2
	- R - rotate inside
	- Cursor aligned to geometry when BC is active automatically
	- C - makes shape the custom shape / w/ text display
	- Flip on Z added
	- Cut w/weight support / fixed


	- Material cut entry (slice only)

	712.3
	- Inset / custom shape parenting fix
	- C - cycle cutters during box / circle draw
	- During T-thick, 1,2 and 3 changes offset
	- Cutters hidden during render / insets too
	- Q Bevel persists across uses
	- Mirror with 1,2,3 and flip with shift +1,2,3
	- Help in N panel
	- Live shape draw checkbox
	- L for make live / persistent
	- Apply slice fix
	- Edit mode snap support
	- Shift + F >> flip shape on Z

	- Make box fixes
	- Mac fixes

	712.4
Sorting Sync

# 711

BC R8 (711)
	- Boolshape sstatus for HOPS connection
	- Edit Mode Live Support
	- Live Blue Box w/selection support
	- Purple Box initial support
	- Icons
	- Redesigned Topbar
	- Redesigned Behavior Panel
	- Shape Submenu Panel
	- Speed Optimizations
	- Bevel / Solidify / Array rememberance
		○ Auto jump to last parameters
	- Cutter Autohiding
	- Modifier removal with key double press during draw
	- Edit mode shift to live cut.
	- Quad Corners togglable
Neutral Grey Box Return

## 700 - 710

HOPS R2
New F6
Slash fix for boxcutter
bugs

BC R2
Array fix.
Bugfixes

BC R3
Bevel Clamp fix
Repeat Shape+
Bevel 2d
Array Circle
	- Draws correct
	- Repeat shape
	- Array repeat support
Bevel Segment Update
Context Sensitive Properties in Behavior Panel
	- Bevel
	- Arraycount
Array /Bevel Live Improvements
Doc URLs updated
Geometry Repeat is always possible instead of optional
Slice Improvements with swapping
Sort Modifiers Toggle for BC
Double Quote fix. It’s a 2.8 bpy thing
Modifier Sort fix
	- Now keeps all mods in whichever order desired
	- Press F to flip
	- Bevel shrink fix
	- Array Flip

BC R4
Sort Modifiers Icons added
Tracking of Start mode
Show wire toggle
Blue Box option
Array scale fix

BC R5
Show wire toggle removed
Tthick Added
Make Box added
3d Make Circle added
Initial Offset parameter added
Shift repeat shape support
Lazercut has a sensitivity limit allowing for extrude back to lazercut
Make active added for shift shape creation workflows
Auto center draw circle
Tweak threshold parameter from preferences added for repeat shape

BC r5.5
Slice apply intersect
Edit Mode Blue
Auto Tthick
Alpha is dropped to .2 from .4 for improved drawing
Quad View support
Lazercut fix
Rotation Matrix

BC R6
	- Circle now dissolves center point
	- Pause / Play
		○ Pause play now works better.
		○ Built for working on denser meshes and is faster
		○ Creates and does cuts after draw.
		○ Alternative to instant cut / draw
	- Hotkey is showing before usage / no longer displays panel before use
	- Center draw box is back.
	- Active cut mode now supports all box types.
	- Skip keymapping in batch mode
	- Fix for linked data removal (nondestructive only)
	- Active only rotation fix
		○ Now active only mode keeps rotation accurately
	- Fix for (1-4) Blender API changes.

BC R7
	- Material Cut
	- Material Cut Toggle M Key
	- Grid System
	- D Menu
	- NGON
	- Quick Execute / Auto Lazercut
	- N Panel Update
	- Object Gizmo w/ shift duplicate support

### 0.6.9.0
- 3D cutter
- HUD moved to center of shape
- curve mode unlocked for circle draw
- NGON can be applied to cursor with double click + alt
- holding shift will keep bevel modifier for all shapes

### 0.6.8.0
- BC can multi cut now instead of border system
- BC hotkeys added to preferences tab
- added color preferences for all modes
- cutter origin now snaps to the cursor
- added option for circle to move center to cursor - hotkey D
- added new option to define cut depth from cursor
- added new option to define gray box size
- removed old carve solver from code
- fixed gray box bug when it was not drawing while no object in scene
- new grid system
- wire no longer goes off if it was on before
- W enables/disables wire in all drawing modes
- drawing respects the regions now
- bc mode can be enabled in many 3d windows at once
- fixed curve opengl issue
- added option for drawing modes to always jump to ortho view
- click logo toggles snapping(optional)
- help toggle box
- new help display system

### 0.6.7.0
- fix for mirror selection
- fix for circle cursor placement
- fix for circle operator transformation
- mesh maker for eddit mode added (temporarily removed)
- added way to run operators from menus/calls
- curve mode (tab) for draw operators do not allow to add points now


### 0.6.6.0
- mirror is using 2d region axis now X and Y
- added projecton box(light blue); to use draw cutter in edit mode
- purple box added; allow to cut around the mesh (press Z while drawing)
- BC no longer draws in objs other then mesh
- mirror hotkeys added for curve (1/2/3 in curve modal state)
- snap axi option for curves 'move' mode (shold shift while move / W to swap axis)
- modal scale added for curve operator (press S)
- modal rotate added for curve operator (press R)
- old rotate removed for curve
- fix for gray box mirror
- fix for wire not hiding if draw operator is canceled


### 0.6.5.2
- fix for grey box


### 0.6.5.1
- fix for pie added to preferences (for builds below 2.79)


### 0.6.5.0
- view align operator in (shift+alt+MMB)
- rotation for curve/ngon added (R/shift+R)
- fix for cutting mesh with distance origin placement
- fix for cuting to cursor in local view
- boolean system redesigned:
	- booleans for bordes and box drawing are now separated
	- 'mod' options are removed, added 'apply boolean' instead
- support for new hops step workflow
- fix for 'convert to curve'
- removed fast bmesh method (after Hardops operators speedup it's no longer needed)
- fixed boolean error if just clicked
- cutter removal for booleans and draws separated
- mirror mode for all cutters added(info pie/help)
- logo indicator changed to new one
- hud options for logo and text added in UI preferences


### 0.6.0.0
- slice replaced with slash operator for yellow box cutter
- way to delate or keep cutter mesh after cutting (in D pie menu)
- new boolean option fast bmesh (doesn't support matterial cutting usefull for sculpting or bigger mesh cutts)
- matterial support for all cutters
- new grid system (relative to the zoom)
- new grid display
- ability to rotate box cutter (after drawing press R or shift R)
- new options in D pie menu to select rotation angle
- new way to use booleans with drawing frames if 2 obj are selected
- fixed pivot point for cutter
- fixed a bug with mesh creation if Algin to view or enter edit mode are used
- overlay for options and grid no longer draws when in edit mode
- hotkes blocking scorll has been removed ( we use D pie now)
