# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: document module-level constants

"""Manim chemistry element representation.

This module provides the :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_element.MCElement` dataclass for representing chemical elements.

"""

from dataclasses import dataclass


@dataclass
class MCElement:
    r"""Used to abstract the properties of elements.

    The properties can be overwritten using custom :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_element.MCElement`\ s and
    passing them as a dictionary to the molecule classes.

    Examples
    ---------
    .. manim:: OverwrittenCarbonElement
       :files: acetone_2d.mol

       from manim import *
       from pathlib import Path
       from manim_extensions.chemistry import GraphMolecule, MCElement

       class OverwrittenCarbonElement(Scene):
           def construct(self):
               default = GraphMolecule.molecule_from_string(Path("acetone_2d.mol").read_text(), format="mol")
               custom_carbon = MCElement(symbol="C", color=PURPLE)
               custom = GraphMolecule.molecule_from_string(
                   Path("acetone_2d.mol").read_text(),
                   format="mol",
                   elements_data_dict={"C": custom_carbon},
               )
               molecules = VGroup(default, custom).arrange(RIGHT, buff=1.5)
               self.play(Write(molecules))
               carbons = VGroup(
                   custom.vertices[2], custom.vertices[3], custom.vertices[4]
               )
               self.play(Indicate(carbons))
               self.wait()
    """

    symbol: str | None = None
    name: str | None = None
    atomic_number: int | None = None
    mass: float | None = None
    color: str | None = None
    cpk_color: str | None = None
    jmol_color: str | None = None
    pubchem_color: str | None = None


# Generic Elements
#: Hydrogen (`H`), atomic number 1.
H = MCElement(
    symbol="H",
    name="Hydrogen",
    atomic_number=1,
    mass=1.007,
    color="#ffffff",
)
#: Helium (`He`), atomic number 2.
He = MCElement(
    symbol="He",
    name="Helium",
    atomic_number=2,
    mass=4.002,
    color="#d9ffff",
)
#: Lithium (`Li`), atomic number 3.
Li = MCElement(
    symbol="Li",
    name="Lithium",
    atomic_number=3,
    mass=6.941,
    color="#cc80ff",
)
#: Beryllium (`Be`), atomic number 4.
Be = MCElement(
    symbol="Be",
    name="Beryllium",
    atomic_number=4,
    mass=9.012,
    color="#c2ff00",
)
#: Boron (`B`), atomic number 5.
B = MCElement(
    symbol="B",
    name="Boron",
    atomic_number=5,
    mass=10.811,
    color="#ffb5b5",
)
#: Carbon (`C`), atomic number 6.
C = MCElement(
    symbol="C",
    name="Carbon",
    atomic_number=6,
    mass=12.011,
    color="#909090",
)
#: Nitrogen (`N`), atomic number 7.
N = MCElement(
    symbol="N",
    name="Nitrogen",
    atomic_number=7,
    mass=14.007,
    color="#3050f8",
)
#: Oxygen (`O`), atomic number 8.
O = MCElement(
    symbol="O",
    name="Oxygen",
    atomic_number=8,
    mass=15.999,
    color="#ff0d0d",
)
#: Fluorine (`F`), atomic number 9.
F = MCElement(
    symbol="F",
    name="Fluorine",
    atomic_number=9,
    mass=18.998,
    color="#90e050",
)
#: Neon (`Ne`), atomic number 10.
Ne = MCElement(
    symbol="Ne",
    name="Neon",
    atomic_number=10,
    mass=20.18,
    color="#b3e3f5",
)
#: Sodium (`Na`), atomic number 11.
Na = MCElement(
    symbol="Na",
    name="Sodium",
    atomic_number=11,
    mass=22.99,
    color="#ab5cf2",
)
#: Magnesium (`Mg`), atomic number 12.
Mg = MCElement(
    symbol="Mg",
    name="Magnesium",
    atomic_number=12,
    mass=24.305,
    color="#8aff00",
)
#: Aluminum (`Al`), atomic number 13.
Al = MCElement(
    symbol="Al",
    name="Aluminum",
    atomic_number=13,
    mass=26.982,
    color="#bfa6a6",
)
#: Silicon (`Si`), atomic number 14.
Si = MCElement(
    symbol="Si",
    name="Silicon",
    atomic_number=14,
    mass=28.086,
    color="#f0c8a0",
)
#: Phosphorus (`P`), atomic number 15.
P = MCElement(
    symbol="P",
    name="Phosphorus",
    atomic_number=15,
    mass=30.974,
    color="#ff8000",
)
#: Sulfur (`S`), atomic number 16.
S = MCElement(
    symbol="S",
    name="Sulfur",
    atomic_number=16,
    mass=32.065,
    color="#ffff30",
)
#: Chlorine (`Cl`), atomic number 17.
Cl = MCElement(
    symbol="Cl",
    name="Chlorine",
    atomic_number=17,
    mass=35.453,
    color="#1ff01f",
)
#: Argon (`Ar`), atomic number 18.
Ar = MCElement(
    symbol="Ar",
    name="Argon",
    atomic_number=18,
    mass=39.948,
    color="#80d1e3",
)
#: Potassium (`K`), atomic number 19.
K = MCElement(
    symbol="K",
    name="Potassium",
    atomic_number=19,
    mass=39.098,
    color="#8f40d4",
)
#: Caclium (`Ca`), atomic number 20.
Ca = MCElement(
    symbol="Ca",
    name="Caclium",
    atomic_number=20,
    mass=40.078,
    color="#3dff00",
)
#: Scandium (`Sc`), atomic number 21.
Sc = MCElement(
    symbol="Sc",
    name="Scandium",
    atomic_number=21,
    mass=44.956,
    color="#e6e6e6",
)
#: Titanium (`Ti`), atomic number 22.
Ti = MCElement(
    symbol="Ti",
    name="Titanium",
    atomic_number=22,
    mass=47.867,
    color="#bfc2c7",
)
#: Vanadium (`V`), atomic number 23.
V = MCElement(
    symbol="V",
    name="Vanadium",
    atomic_number=23,
    mass=50.942,
    color="#a6a6ab",
)
#: Chromium (`Cr`), atomic number 24.
Cr = MCElement(
    symbol="Cr",
    name="Chromium",
    atomic_number=24,
    mass=51.996,
    color="#8a99c7",
)
#: Manganese (`Mn`), atomic number 25.
Mn = MCElement(
    symbol="Mn",
    name="Manganese",
    atomic_number=25,
    mass=54.938,
    color="#9c7ac7",
)
#: Iron (`Fe`), atomic number 26.
Fe = MCElement(
    symbol="Fe",
    name="Iron",
    atomic_number=26,
    mass=55.845,
    color="#e06633",
)
#: Cobalt (`Co`), atomic number 27.
Co = MCElement(
    symbol="Co",
    name="Cobalt",
    atomic_number=27,
    mass=58.933,
    color="#f090a0",
)
#: Nickel (`Ni`), atomic number 28.
Ni = MCElement(
    symbol="Ni",
    name="Nickel",
    atomic_number=28,
    mass=58.693,
    color="#50d050",
)
#: Copper (`Cu`), atomic number 29.
Cu = MCElement(
    symbol="Cu",
    name="Copper",
    atomic_number=29,
    mass=63.546,
    color="#c88033",
)
#: Zinc (`Zn`), atomic number 30.
Zn = MCElement(
    symbol="Zn",
    name="Zinc",
    atomic_number=30,
    mass=65.38,
    color="#7d80b0",
)
#: Gallium (`Ga`), atomic number 31.
Ga = MCElement(
    symbol="Ga",
    name="Gallium",
    atomic_number=31,
    mass=69.723,
    color="#c28f8f",
)
#: Germanium (`Ge`), atomic number 32.
Ge = MCElement(
    symbol="Ge",
    name="Germanium",
    atomic_number=32,
    mass=72.64,
    color="#668f8f",
)
#: Arsenic (`As`), atomic number 33.
As = MCElement(
    symbol="As",
    name="Arsenic",
    atomic_number=33,
    mass=74.922,
    color="#bd80e3",
)
#: Selenium (`Se`), atomic number 34.
Se = MCElement(
    symbol="Se",
    name="Selenium",
    atomic_number=34,
    mass=78.96,
    color="#ffa100",
)
#: Bromine (`Br`), atomic number 35.
Br = MCElement(
    symbol="Br",
    name="Bromine",
    atomic_number=35,
    mass=79.904,
    color="#a62929",
)
#: Krypton (`Kr`), atomic number 36.
Kr = MCElement(
    symbol="Kr",
    name="Krypton",
    atomic_number=36,
    mass=83.798,
    color="#5cb8d1",
)
#: Rubidium (`Rb`), atomic number 37.
Rb = MCElement(
    symbol="Rb",
    name="Rubidium",
    atomic_number=37,
    mass=85.468,
    color="#702eb0",
)
#: Strontium (`Sr`), atomic number 38.
Sr = MCElement(
    symbol="Sr",
    name="Strontium",
    atomic_number=38,
    mass=87.62,
    color="#00ff00",
)
#: Yttrium (`Y`), atomic number 39.
Y = MCElement(
    symbol="Y",
    name="Yttrium",
    atomic_number=39,
    mass=88.906,
    color="#94ffff",
)
#: Zirconium (`Zr`), atomic number 40.
Zr = MCElement(
    symbol="Zr",
    name="Zirconium",
    atomic_number=40,
    mass=91.224,
    color="#94e0e0",
)
#: Niobium (`Nb`), atomic number 41.
Nb = MCElement(
    symbol="Nb",
    name="Niobium",
    atomic_number=41,
    mass=92.906,
    color="#73c2c9",
)
#: Molybdenum (`Mo`), atomic number 42.
Mo = MCElement(
    symbol="Mo",
    name="Molybdenum",
    atomic_number=42,
    mass=95.96,
    color="#54b5b5",
)
#: Technitium (`Tc`), atomic number 43.
Tc = MCElement(
    symbol="Tc",
    name="Technitium",
    atomic_number=43,
    mass=98.0,
    color="#3b9e9e",
)
#: Ruthenium (`Ru`), atomic number 44.
Ru = MCElement(
    symbol="Ru",
    name="Ruthenium",
    atomic_number=44,
    mass=101.07,
    color="#248f8f",
)
#: Rhodium (`Rh`), atomic number 45.
Rh = MCElement(
    symbol="Rh",
    name="Rhodium",
    atomic_number=45,
    mass=102.906,
    color="#0a7d8c",
)
#: Palladium (`Pd`), atomic number 46.
Pd = MCElement(
    symbol="Pd",
    name="Palladium",
    atomic_number=46,
    mass=106.42,
    color="#006985",
)
#: Silver (`Ag`), atomic number 47.
Ag = MCElement(
    symbol="Ag",
    name="Silver",
    atomic_number=47,
    mass=107.868,
    color="#c0c0c0",
)
#: Cadmium (`Cd`), atomic number 48.
Cd = MCElement(
    symbol="Cd",
    name="Cadmium",
    atomic_number=48,
    mass=112.411,
    color="#ffd98f",
)
#: Indium (`In`), atomic number 49.
In = MCElement(
    symbol="In",
    name="Indium",
    atomic_number=49,
    mass=114.818,
    color="#a67573",
)
#: Tin (`Sn`), atomic number 50.
Sn = MCElement(
    symbol="Sn",
    name="Tin",
    atomic_number=50,
    mass=118.71,
    color="#668080",
)
#: Antimony (`Sb`), atomic number 51.
Sb = MCElement(
    symbol="Sb",
    name="Antimony",
    atomic_number=51,
    mass=121.76,
    color="#9e63b5",
)
#: Tellerium (`Te`), atomic number 52.
Te = MCElement(
    symbol="Te",
    name="Tellerium",
    atomic_number=52,
    mass=127.6,
    color="#d47a00",
)
#: Iodine (`I`), atomic number 53.
I = MCElement(
    symbol="I",
    name="Iodine",
    atomic_number=53,
    mass=126.904,
    color="#940094",
)
#: Xeon (`Xe`), atomic number 54.
Xe = MCElement(
    symbol="Xe",
    name="Xeon",
    atomic_number=54,
    mass=131.293,
    color="#429eb0",
)
#: Cesium (`Cs`), atomic number 55.
Cs = MCElement(
    symbol="Cs",
    name="Cesium",
    atomic_number=55,
    mass=132.905,
    color="#57178f",
)
#: Barium (`Ba`), atomic number 56.
Ba = MCElement(
    symbol="Ba",
    name="Barium",
    atomic_number=56,
    mass=137.327,
    color="#00c900",
)
#: Lanthanum (`La`), atomic number 57.
La = MCElement(
    symbol="La",
    name="Lanthanum",
    atomic_number=57,
    mass=138.905,
    color="#70d4ff",
)
#: Cerium (`Ce`), atomic number 58.
Ce = MCElement(
    symbol="Ce",
    name="Cerium",
    atomic_number=58,
    mass=140.116,
    color="#ffffc7",
)
#: Praseodymium (`Pr`), atomic number 59.
Pr = MCElement(
    symbol="Pr",
    name="Praseodymium",
    atomic_number=59,
    mass=140.908,
    color="#d9ffc7",
)
#: Neodymium (`Nd`), atomic number 60.
Nd = MCElement(
    symbol="Nd",
    name="Neodymium",
    atomic_number=60,
    mass=144.242,
    color="#c7ffc7",
)
#: Promethium (`Pm`), atomic number 61.
Pm = MCElement(
    symbol="Pm",
    name="Promethium",
    atomic_number=61,
    mass=145.0,
    color="#a3ffc7",
)
#: Samarium (`Sm`), atomic number 62.
Sm = MCElement(
    symbol="Sm",
    name="Samarium",
    atomic_number=62,
    mass=150.36,
    color="#8fffc7",
)
#: Europium (`Eu`), atomic number 63.
Eu = MCElement(
    symbol="Eu",
    name="Europium",
    atomic_number=63,
    mass=151.964,
    color="#61ffc7",
)
#: Gadolinium (`Gd`), atomic number 64.
Gd = MCElement(
    symbol="Gd",
    name="Gadolinium",
    atomic_number=64,
    mass=157.25,
    color="#45ffc7",
)
#: Terbium (`Tb`), atomic number 65.
Tb = MCElement(
    symbol="Tb",
    name="Terbium",
    atomic_number=65,
    mass=158.925,
    color="#30ffc7",
)
#: Dysprosium (`Dy`), atomic number 66.
Dy = MCElement(
    symbol="Dy",
    name="Dysprosium",
    atomic_number=66,
    mass=162.5,
    color="#1fffc7",
)
#: Holmium (`Ho`), atomic number 67.
Ho = MCElement(
    symbol="Ho",
    name="Holmium",
    atomic_number=67,
    mass=164.93,
    color="#00ff9c",
)
#: Erbium (`Er`), atomic number 68.
Er = MCElement(
    symbol="Er",
    name="Erbium",
    atomic_number=68,
    mass=167.259,
    color="#00e675",
)
#: Thulium (`Tm`), atomic number 69.
Tm = MCElement(
    symbol="Tm",
    name="Thulium",
    atomic_number=69,
    mass=168.934,
    color="#00d452",
)
#: Ytterbium (`Yb`), atomic number 70.
Yb = MCElement(
    symbol="Yb",
    name="Ytterbium",
    atomic_number=70,
    mass=173.054,
    color="#00bf38",
)
#: Lutetium (`Lu`), atomic number 71.
Lu = MCElement(
    symbol="Lu",
    name="Lutetium",
    atomic_number=71,
    mass=174.967,
    color="#00ab24",
)
#: Hafnium (`Hf`), atomic number 72.
Hf = MCElement(
    symbol="Hf",
    name="Hafnium",
    atomic_number=72,
    mass=178.49,
    color="#4dc2ff",
)
#: Tantalum (`Ta`), atomic number 73.
Ta = MCElement(
    symbol="Ta",
    name="Tantalum",
    atomic_number=73,
    mass=180.948,
    color="#4da6ff",
)
#: Tungsten (`W`), atomic number 74.
W = MCElement(
    symbol="W",
    name="Tungsten",
    atomic_number=74,
    mass=183.84,
    color="#2194d6",
)
#: Rhenium (`Re`), atomic number 75.
Re = MCElement(
    symbol="Re",
    name="Rhenium",
    atomic_number=75,
    mass=186.207,
    color="#267dab",
)
#: Osmium (`Os`), atomic number 76.
Os = MCElement(
    symbol="Os",
    name="Osmium",
    atomic_number=76,
    mass=190.23,
    color="#266696",
)
#: Iridium (`Ir`), atomic number 77.
Ir = MCElement(
    symbol="Ir",
    name="Iridium",
    atomic_number=77,
    mass=192.217,
    color="#175487",
)
#: Platinum (`Pt`), atomic number 78.
Pt = MCElement(
    symbol="Pt",
    name="Platinum",
    atomic_number=78,
    mass=195.084,
    color="#d0d0e0",
)
#: Gold (`Au`), atomic number 79.
Au = MCElement(
    symbol="Au",
    name="Gold",
    atomic_number=79,
    mass=196.967,
    color="#ffd123",
)
#: Mercury (`Hg`), atomic number 80.
Hg = MCElement(
    symbol="Hg",
    name="Mercury",
    atomic_number=80,
    mass=200.59,
    color="#b8b8d0",
)
#: Thallium (`Tl`), atomic number 81.
Tl = MCElement(
    symbol="Tl",
    name="Thallium",
    atomic_number=81,
    mass=204.383,
    color="#a6544d",
)
#: Lead (`Pb`), atomic number 82.
Pb = MCElement(
    symbol="Pb",
    name="Lead",
    atomic_number=82,
    mass=207.2,
    color="#575961",
)
#: Bismuth (`Bi`), atomic number 83.
Bi = MCElement(
    symbol="Bi",
    name="Bismuth",
    atomic_number=83,
    mass=208.98,
    color="#9e4fb5",
)
#: Polonium (`Po`), atomic number 84.
Po = MCElement(
    symbol="Po",
    name="Polonium",
    atomic_number=84,
    mass=210.0,
    color="#ab5c00",
)
#: Astatine (`At`), atomic number 85.
At = MCElement(
    symbol="At",
    name="Astatine",
    atomic_number=85,
    mass=210.0,
    color="#754f45",
)
#: Radon (`Rn`), atomic number 86.
Rn = MCElement(
    symbol="Rn",
    name="Radon",
    atomic_number=86,
    mass=222.0,
    color="#428296",
)
#: Francium (`Fr`), atomic number 87.
Fr = MCElement(
    symbol="Fr",
    name="Francium",
    atomic_number=87,
    mass=223.0,
    color="#420066",
)
#: Radium (`Ra`), atomic number 88.
Ra = MCElement(
    symbol="Ra",
    name="Radium",
    atomic_number=88,
    mass=226.0,
    color="#007d00",
)
#: Actinium (`Ac`), atomic number 89.
Ac = MCElement(
    symbol="Ac",
    name="Actinium",
    atomic_number=89,
    mass=227.0,
    color="#70abfa",
)
#: Thorium (`Th`), atomic number 90.
Th = MCElement(
    symbol="Th",
    name="Thorium",
    atomic_number=90,
    mass=232.038,
    color="#00baff",
)
#: Protactinium (`Pa`), atomic number 91.
Pa = MCElement(
    symbol="Pa",
    name="Protactinium",
    atomic_number=91,
    mass=231.036,
    color="#00a1ff",
)
#: Uranium (`U`), atomic number 92.
U = MCElement(
    symbol="U",
    name="Uranium",
    atomic_number=92,
    mass=238.029,
    color="#008fff",
)
#: Neptunium (`Np`), atomic number 93.
Np = MCElement(
    symbol="Np",
    name="Neptunium",
    atomic_number=93,
    mass=237.0,
    color="#0080ff",
)
#: Plutonium (`Pu`), atomic number 94.
Pu = MCElement(
    symbol="Pu",
    name="Plutonium",
    atomic_number=94,
    mass=244.0,
    color="#006bff",
)
#: Americium (`Am`), atomic number 95.
Am = MCElement(
    symbol="Am",
    name="Americium",
    atomic_number=95,
    mass=243.0,
    color="#545cf2",
)
#: Curium (`Cm`), atomic number 96.
Cm = MCElement(
    symbol="Cm",
    name="Curium",
    atomic_number=96,
    mass=247.0,
    color="#785ce3",
)
#: Berkelium (`Bk`), atomic number 97.
Bk = MCElement(
    symbol="Bk",
    name="Berkelium",
    atomic_number=97,
    mass=247.0,
    color="#8a4fe3",
)
#: Californium (`Cf`), atomic number 98.
Cf = MCElement(
    symbol="Cf",
    name="Californium",
    atomic_number=98,
    mass=251.0,
    color="#a136d4",
)
#: Einsteinium (`Es`), atomic number 99.
Es = MCElement(
    symbol="Es",
    name="Einsteinium",
    atomic_number=99,
    mass=252.0,
    color="#b31fd4",
)
#: Fermium (`Fm`), atomic number 100.
Fm = MCElement(
    symbol="Fm",
    name="Fermium",
    atomic_number=100,
    mass=257.0,
    color="#b31fba",
)
#: Mendelevium (`Md`), atomic number 101.
Md = MCElement(
    symbol="Md",
    name="Mendelevium",
    atomic_number=101,
    mass=258.0,
    color="#b30da6",
)
#: Nobelium (`No`), atomic number 102.
No = MCElement(
    symbol="No",
    name="Nobelium",
    atomic_number=102,
    mass=259.0,
    color="#bd0d87",
)
#: Lawrencium (`Lr`), atomic number 103.
Lr = MCElement(
    symbol="Lr",
    name="Lawrencium",
    atomic_number=103,
    mass=262.0,
    color="#c70066",
)
#: Rutherfordium (`Rf`), atomic number 104.
Rf = MCElement(
    symbol="Rf",
    name="Rutherfordium",
    atomic_number=104,
    mass=261.0,
    color="#cc0059",
)
#: Dubnium (`Db`), atomic number 105.
Db = MCElement(
    symbol="Db",
    name="Dubnium",
    atomic_number=105,
    mass=262.0,
    color="#d1004f",
)
#: Seaborgium (`Sg`), atomic number 106.
Sg = MCElement(
    symbol="Sg",
    name="Seaborgium",
    atomic_number=106,
    mass=266.0,
    color="#d90045",
)
#: Bohrium (`Bh`), atomic number 107.
Bh = MCElement(
    symbol="Bh",
    name="Bohrium",
    atomic_number=107,
    mass=264.0,
    color="#e00038",
)
#: Hassium (`Hs`), atomic number 108.
Hs = MCElement(
    symbol="Hs",
    name="Hassium",
    atomic_number=108,
    mass=267.0,
    color="#e6002e",
)
#: Meitnerium (`Mt`), atomic number 109.
Mt = MCElement(
    symbol="Mt",
    name="Meitnerium",
    atomic_number=109,
    mass=268.0,
    color="#eb0026",
)
#: Darmstadtium (`Ds`), atomic number 110.
Ds = MCElement(
    symbol="Ds",
    name="Darmstadtium",
    atomic_number=110,
    mass=271.0,
    color="#eb0026",
)
#: Roentgenium (`Rg`), atomic number 111.
Rg = MCElement(
    symbol="Rg",
    name="Roentgenium",
    atomic_number=111,
    mass=272.0,
    color="#eb0026",
)
#: Copernicium (`Cn`), atomic number 112.
Cn = MCElement(
    symbol="Cn",
    name="Copernicium",
    atomic_number=112,
    mass=285.0,
    color="#eb0026",
)
#: Nihonium (`Nh`), atomic number 113.
Nh = MCElement(
    symbol="Nh",
    name="Nihonium",
    atomic_number=113,
    mass=284.0,
    color="#eb0026",
)
#: Flerovium (`Fl`), atomic number 114.
Fl = MCElement(
    symbol="Fl",
    name="Flerovium",
    atomic_number=114,
    mass=289.0,
    color="#eb0026",
)
#: Moscovium (`Mc`), atomic number 115.
Mc = MCElement(
    symbol="Mc",
    name="Moscovium",
    atomic_number=115,
    mass=288.0,
    color="#eb0026",
)
#: Livermorium (`Lv`), atomic number 116.
Lv = MCElement(
    symbol="Lv",
    name="Livermorium",
    atomic_number=116,
    mass=292.0,
    color="#eb0026",
)
#: Tennessine (`Ts`), atomic number 117.
Ts = MCElement(
    symbol="Ts",
    name="Tennessine",
    atomic_number=117,
    mass=295.0,
    color="#eb0026",
)
#: Oganesson (`Og`), atomic number 118.
Og = MCElement(
    symbol="Og",
    name="Oganesson",
    atomic_number=118,
    mass=294.0,
    color="#eb0026",
)


#: Mapping from element symbol to the corresponding :class:~manim_extensions.chemistry.manim_chemistry_molecule.mc_element.MCElement.
MC_ELEMENT_DICT = {
    "H": H,
    "He": He,
    "Li": Li,
    "Be": Be,
    "B": B,
    "C": C,
    "N": N,
    "O": O,
    "F": F,
    "Ne": Ne,
    "Na": Na,
    "Mg": Mg,
    "Al": Al,
    "Si": Si,
    "P": P,
    "S": S,
    "Cl": Cl,
    "Ar": Ar,
    "K": K,
    "Ca": Ca,
    "Sc": Sc,
    "Ti": Ti,
    "V": V,
    "Cr": Cr,
    "Mn": Mn,
    "Fe": Fe,
    "Co": Co,
    "Ni": Ni,
    "Cu": Cu,
    "Zn": Zn,
    "Ga": Ga,
    "Ge": Ge,
    "As": As,
    "Se": Se,
    "Br": Br,
    "Kr": Kr,
    "Rb": Rb,
    "Sr": Sr,
    "Y": Y,
    "Zr": Zr,
    "Nb": Nb,
    "Mo": Mo,
    "Tc": Tc,
    "Ru": Ru,
    "Rh": Rh,
    "Pd": Pd,
    "Ag": Ag,
    "Cd": Cd,
    "In": In,
    "Sn": Sn,
    "Sb": Sb,
    "Te": Te,
    "I": I,
    "Xe": Xe,
    "Cs": Cs,
    "Ba": Ba,
    "La": La,
    "Ce": Ce,
    "Pr": Pr,
    "Nd": Nd,
    "Pm": Pm,
    "Sm": Sm,
    "Eu": Eu,
    "Gd": Gd,
    "Tb": Tb,
    "Dy": Dy,
    "Ho": Ho,
    "Er": Er,
    "Tm": Tm,
    "Yb": Yb,
    "Lu": Lu,
    "Hf": Hf,
    "Ta": Ta,
    "W": W,
    "Re": Re,
    "Os": Os,
    "Ir": Ir,
    "Pt": Pt,
    "Au": Au,
    "Hg": Hg,
    "Tl": Tl,
    "Pb": Pb,
    "Bi": Bi,
    "Po": Po,
    "At": At,
    "Rn": Rn,
    "Fr": Fr,
    "Ra": Ra,
    "Ac": Ac,
    "Th": Th,
    "Pa": Pa,
    "U": U,
    "Np": Np,
    "Pu": Pu,
    "Am": Am,
    "Cm": Cm,
    "Bk": Bk,
    "Cf": Cf,
    "Es": Es,
    "Fm": Fm,
    "Md": Md,
    "No": No,
    "Lr": Lr,
    "Rf": Rf,
    "Db": Db,
    "Sg": Sg,
    "Bh": Bh,
    "Hs": Hs,
    "Mt": Mt,
    "Ds": Ds,
    "Rg": Rg,
    "Cn": Cn,
    "Nh": Nh,
    "Fl": Fl,
    "Mc": Mc,
    "Lv": Lv,
    "Ts": Ts,
    "Og": Og,
}
