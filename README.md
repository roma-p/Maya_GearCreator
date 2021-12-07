# Gear Creator

Gear Creator is a Maya plugin to easily create / edit complex gear netowks.
The plugin is still in early alpha.

![Alt text](etc/main_screenshot_1.jpg?raw=true "gear_creator")

## Installation

- download the src folder and copy/paste it either: 
	+ in your Maya installation scripts folder. 
	+ in a custom folder
- if you copy the sources in a custom folder, you need to define it in settings.json:
  eg for windows:
  ```json
  {
  	"installation_folder": "D:/custom_scripts/"
  }
  ```
- using the maya script editor, launch "__main__.py"

## Usage

Rather than creating a gear at a time and then positionning manually, the philosophy of this plugin is not so much of creating individual gears but complete gear networks. Therefore:
- Gears are created from a parent gear, they can't be created freely.
- Their placement is automatic: 
	+ they can only be rotated around neighour gears
	+ changing the radius / internal radius will adjust position for current gear / rest of the network

![Alt text](etc/gear_sc_1.png?raw=true "single_gear_edition")


- A **gear chain** is a ensemble of gears directly conncected to each other.
- A **gear network** consists of multiple gear chains linked each other by rods.

Some of the parameter are not configurable for individual gear but for the overall gear chain:
- Teeth Number:
	+ You can't set the number of teeth for an individual gear
	+ Rather, you can set the width of the teeth for the overall chain
	+ Teeth number is then automatically calculated for each gear so that they can all fit into each other.
- Height:
	+ The height of the gears can be changed at the chain level
	+ The min / max height is caculated from all the rods present in the chain.

![Alt text](etc/gear_sc_2.png?raw=true "gear_chain_edition")

- Once the plugin is launched, the gear creator IHM will pop, you can dock it if you want to.
- IHM consists of three pages:
	+ **gear networks page**: list all the network of the scene, you can rename / hide them.
	+ **gear chains page**: list all the chains of the current network, will also temporarily color them for better comprehension of the network. You can rename / hide / edit the chains from here.
	+ **object page (either gear or rod)**: from here you can rename / hide / edit the current object. Neighbour gears will also be temporarily colored.
- As long as no element of a gear network is selected, only the "gear networks" page is accessible
- Once you selected an object of the network:
	+ the "object" page will be shown.
	+ gear "chains page" will be accessible.

You can quit the plugin, the scene and maya safely! All gear creator infos are stored inside the scene, so you can edit your networks later using the plugin.
(at least you should)

## Next!

(by criticity)
- Fix gear teeth collision bug.
- Still lots of bug to fix.
- Animation!
- Bevel option for gears and rods
- Multiple orientation possible for gears (parrallel, - 90°, +90°)
- Multiple gear shapes
- Snapping options for positions of the gears.

## Misc

### Maya Wrapper
Coding this library, I tried to create a small library to wrap Maya Transform nodes for pymel.
- The library can be found at src/Maya_GearCreator/maya_wrapper
- Usage example can be found at etc/maya_wrapper_ex.py
