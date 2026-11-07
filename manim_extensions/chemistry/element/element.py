# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pandas (chemistry extra)
# patched: document module-level constants

"""Chemical element data structure."""

from dataclasses import dataclass
from typing import Self

from ...utils.deps import require


class Element:
    """Chemical element data.

    Parameters
    ----------
    symbol
        Chemical symbol of the element. 
    name
        Full name of the element. 
    atomic_number
        Atomic number of the element. 
    mass
        Atomic mass of the element. 
    color
        Display color of the element. Falls back to ``"#ff00ff"`` when
        falsy. 
    """
    def __repr__(self) -> str:
        return f"Element {self.atomic_number}: {self.name} ({self.symbol})"

    def __init__(
        self,
        symbol: str = "H",
        name: str = "H",
        atomic_number: int = 1,
        mass: float = 1.008,
        color: str | None = "#FFFFFF",
    ):
        """Initialize the Element instance."""
        self.symbol = symbol
        self.name = name
        self.atomic_number = atomic_number
        self.mass = mass
        self.color = color or "#ff00ff"

    def from_csv_file(filename: str, element: str | int) -> Self:
        """Create an :class:`~manim_extensions.chemistry.element.element.Element` from a CSV file.

        Parameters
        ----------
        filename
            Path to the CSV file containing element data.
        element
            Symbol or atomic number of the element to look up.

        Returns
        -------
            A Element instance representing the result.

        Raises
        ------
        Exception
            Raised when ``element`` is neither a valid symbol nor an atomic
            number below 118, or when no matching element is found in the
            CSV file.
        """
        use_valid_reference_string = f"What are you doing? Pass a valid atomic reference. {element} is NOT a valid reference"
        pd = require("chemistry", "pandas")
        data = pd.read_csv(filename, index_col=False)

        if isinstance(element, str):
            search_column = "Symbol"

        elif isinstance(element, int) and element < 118:
            search_column = "AtomicNumber"

        else:
            raise Exception(use_valid_reference_string)

        subdata = data.loc[data[search_column] == element]

        if subdata.empty:
            raise Exception(use_valid_reference_string)

        element_data = subdata.squeeze().to_dict()

        return Element(
            symbol=element_data["Symbol"],
            name=element_data["Name"],
            atomic_number=element_data["AtomicNumber"],
            mass=element_data["AtomicMass"],
            color=element_data["Color"],
        )


@dataclass
class GenericElement:
    """Data for a chemical element (symbol, name, atomic number, mass, CPK color)."""

    symbol: str
    name: str
    atomic_number: int
    mass: float
    cpk_color: str


# Generic Elements
#: Hydrogen (`H`), atomic number 1.
H = GenericElement("H", "Hydrogen", 1, 1.007, "#ffffff")
#: Helium (`He`), atomic number 2.
He = GenericElement("He", "Helium", 2, 4.002, "#d9ffff")
#: Lithium (`Li`), atomic number 3.
Li = GenericElement("Li", "Lithium", 3, 6.941, "#cc80ff")
#: Beryllium (`Be`), atomic number 4.
Be = GenericElement("Be", "Beryllium", 4, 9.012, "#c2ff00")
#: Boron (`B`), atomic number 5.
B = GenericElement("B", "Boron", 5, 10.811, "#ffb5b5")
#: Carbon (`C`), atomic number 6.
C = GenericElement("C", "Carbon", 6, 12.011, "#909090")
#: Nitrogen (`N`), atomic number 7.
N = GenericElement("N", "Nitrogen", 7, 14.007, "#3050f8")
#: Oxygen (`O`), atomic number 8.
O = GenericElement("O", "Oxygen", 8, 15.999, "#ff0d0d")
#: Fluorine (`F`), atomic number 9.
F = GenericElement("F", "Fluorine", 9, 18.998, "#90e050")
#: Neon (`Ne`), atomic number 10.
Ne = GenericElement("Ne", "Neon", 10, 20.18, "#b3e3f5")
#: Sodium (`Na`), atomic number 11.
Na = GenericElement("Na", "Sodium", 11, 22.99, "#ab5cf2")
#: Magnesium (`Mg`), atomic number 12.
Mg = GenericElement("Mg", "Magnesium", 12, 24.305, "#8aff00")
#: Aluminum (`Al`), atomic number 13.
Al = GenericElement("Al", "Aluminum", 13, 26.982, "#bfa6a6")
#: Silicon (`Si`), atomic number 14.
Si = GenericElement("Si", "Silicon", 14, 28.086, "#f0c8a0")
#: Phosphorus (`P`), atomic number 15.
P = GenericElement("P", "Phosphorus", 15, 30.974, "#ff8000")
#: Sulfur (`S`), atomic number 16.
S = GenericElement("S", "Sulfur", 16, 32.065, "#ffff30")
#: Chlorine (`Cl`), atomic number 17.
Cl = GenericElement("Cl", "Chlorine", 17, 35.453, "#1ff01f")
#: Argon (`Ar`), atomic number 18.
Ar = GenericElement("Ar", "Argon", 18, 39.948, "#80d1e3")
#: Potassium (`K`), atomic number 19.
K = GenericElement("K", "Potassium", 19, 39.098, "#8f40d4")
#: Caclium (`Ca`), atomic number 20.
Ca = GenericElement("Ca", "Caclium", 20, 40.078, "#3dff00")
#: Scandium (`Sc`), atomic number 21.
Sc = GenericElement("Sc", "Scandium", 21, 44.956, "#e6e6e6")
#: Titanium (`Ti`), atomic number 22.
Ti = GenericElement("Ti", "Titanium", 22, 47.867, "#bfc2c7")
#: Vanadium (`V`), atomic number 23.
V = GenericElement("V", "Vanadium", 23, 50.942, "#a6a6ab")
#: Chromium (`Cr`), atomic number 24.
Cr = GenericElement("Cr", "Chromium", 24, 51.996, "#8a99c7")
#: Manganese (`Mn`), atomic number 25.
Mn = GenericElement("Mn", "Manganese", 25, 54.938, "#9c7ac7")
#: Iron (`Fe`), atomic number 26.
Fe = GenericElement("Fe", "Iron", 26, 55.845, "#e06633")
#: Cobalt (`Co`), atomic number 27.
Co = GenericElement("Co", "Cobalt", 27, 58.933, "#f090a0")
#: Nickel (`Ni`), atomic number 28.
Ni = GenericElement("Ni", "Nickel", 28, 58.693, "#50d050")
#: Copper (`Cu`), atomic number 29.
Cu = GenericElement("Cu", "Copper", 29, 63.546, "#c88033")
#: Zinc (`Zn`), atomic number 30.
Zn = GenericElement("Zn", "Zinc", 30, 65.38, "#7d80b0")
#: Gallium (`Ga`), atomic number 31.
Ga = GenericElement("Ga", "Gallium", 31, 69.723, "#c28f8f")
#: Germanium (`Ge`), atomic number 32.
Ge = GenericElement("Ge", "Germanium", 32, 72.64, "#668f8f")
#: Arsenic (`As`), atomic number 33.
As = GenericElement("As", "Arsenic", 33, 74.922, "#bd80e3")
#: Selenium (`Se`), atomic number 34.
Se = GenericElement("Se", "Selenium", 34, 78.96, "#ffa100")
#: Bromine (`Br`), atomic number 35.
Br = GenericElement("Br", "Bromine", 35, 79.904, "#a62929")
#: Krypton (`Kr`), atomic number 36.
Kr = GenericElement("Kr", "Krypton", 36, 83.798, "#5cb8d1")
#: Rubidium (`Rb`), atomic number 37.
Rb = GenericElement("Rb", "Rubidium", 37, 85.468, "#702eb0")
#: Strontium (`Sr`), atomic number 38.
Sr = GenericElement("Sr", "Strontium", 38, 87.62, "#00ff00")
#: Yttrium (`Y`), atomic number 39.
Y = GenericElement("Y", "Yttrium", 39, 88.906, "#94ffff")
#: Zirconium (`Zr`), atomic number 40.
Zr = GenericElement("Zr", "Zirconium", 40, 91.224, "#94e0e0")
#: Niobium (`Nb`), atomic number 41.
Nb = GenericElement("Nb", "Niobium", 41, 92.906, "#73c2c9")
#: Molybdenum (`Mo`), atomic number 42.
Mo = GenericElement("Mo", "Molybdenum", 42, 95.96, "#54b5b5")
#: Technitium (`Tc`), atomic number 43.
Tc = GenericElement("Tc", "Technitium", 43, 98.0, "#3b9e9e")
#: Ruthenium (`Ru`), atomic number 44.
Ru = GenericElement("Ru", "Ruthenium", 44, 101.07, "#248f8f")
#: Rhodium (`Rh`), atomic number 45.
Rh = GenericElement("Rh", "Rhodium", 45, 102.906, "#0a7d8c")
#: Palladium (`Pd`), atomic number 46.
Pd = GenericElement("Pd", "Palladium", 46, 106.42, "#006985")
#: Silver (`Ag`), atomic number 47.
Ag = GenericElement("Ag", "Silver", 47, 107.868, "#c0c0c0")
#: Cadmium (`Cd`), atomic number 48.
Cd = GenericElement("Cd", "Cadmium", 48, 112.411, "#ffd98f")
#: Indium (`In`), atomic number 49.
In = GenericElement("In", "Indium", 49, 114.818, "#a67573")
#: Tin (`Sn`), atomic number 50.
Sn = GenericElement("Sn", "Tin", 50, 118.71, "#668080")
#: Antimony (`Sb`), atomic number 51.
Sb = GenericElement("Sb", "Antimony", 51, 121.76, "#9e63b5")
#: Tellerium (`Te`), atomic number 52.
Te = GenericElement("Te", "Tellerium", 52, 127.6, "#d47a00")
#: Iodine (`I`), atomic number 53.
I = GenericElement("I", "Iodine", 53, 126.904, "#940094")
#: Xeon (`Xe`), atomic number 54.
Xe = GenericElement("Xe", "Xeon", 54, 131.293, "#429eb0")
#: Cesium (`Cs`), atomic number 55.
Cs = GenericElement("Cs", "Cesium", 55, 132.905, "#57178f")
#: Barium (`Ba`), atomic number 56.
Ba = GenericElement("Ba", "Barium", 56, 137.327, "#00c900")
#: Lanthanum (`La`), atomic number 57.
La = GenericElement("La", "Lanthanum", 57, 138.905, "#70d4ff")
#: Cerium (`Ce`), atomic number 58.
Ce = GenericElement("Ce", "Cerium", 58, 140.116, "#ffffc7")
#: Praseodymium (`Pr`), atomic number 59.
Pr = GenericElement("Pr", "Praseodymium", 59, 140.908, "#d9ffc7")
#: Neodymium (`Nd`), atomic number 60.
Nd = GenericElement("Nd", "Neodymium", 60, 144.242, "#c7ffc7")
#: Promethium (`Pm`), atomic number 61.
Pm = GenericElement("Pm", "Promethium", 61, 145.0, "#a3ffc7")
#: Samarium (`Sm`), atomic number 62.
Sm = GenericElement("Sm", "Samarium", 62, 150.36, "#8fffc7")
#: Europium (`Eu`), atomic number 63.
Eu = GenericElement("Eu", "Europium", 63, 151.964, "#61ffc7")
#: Gadolinium (`Gd`), atomic number 64.
Gd = GenericElement("Gd", "Gadolinium", 64, 157.25, "#45ffc7")
#: Terbium (`Tb`), atomic number 65.
Tb = GenericElement("Tb", "Terbium", 65, 158.925, "#30ffc7")
#: Dysprosium (`Dy`), atomic number 66.
Dy = GenericElement("Dy", "Dysprosium", 66, 162.5, "#1fffc7")
#: Holmium (`Ho`), atomic number 67.
Ho = GenericElement("Ho", "Holmium", 67, 164.93, "#00ff9c")
#: Erbium (`Er`), atomic number 68.
Er = GenericElement("Er", "Erbium", 68, 167.259, "#00e675")
#: Thulium (`Tm`), atomic number 69.
Tm = GenericElement("Tm", "Thulium", 69, 168.934, "#00d452")
#: Ytterbium (`Yb`), atomic number 70.
Yb = GenericElement("Yb", "Ytterbium", 70, 173.054, "#00bf38")
#: Lutetium (`Lu`), atomic number 71.
Lu = GenericElement("Lu", "Lutetium", 71, 174.967, "#00ab24")
#: Hafnium (`Hf`), atomic number 72.
Hf = GenericElement("Hf", "Hafnium", 72, 178.49, "#4dc2ff")
#: Tantalum (`Ta`), atomic number 73.
Ta = GenericElement("Ta", "Tantalum", 73, 180.948, "#4da6ff")
#: Tungsten (`W`), atomic number 74.
W = GenericElement("W", "Tungsten", 74, 183.84, "#2194d6")
#: Rhenium (`Re`), atomic number 75.
Re = GenericElement("Re", "Rhenium", 75, 186.207, "#267dab")
#: Osmium (`Os`), atomic number 76.
Os = GenericElement("Os", "Osmium", 76, 190.23, "#266696")
#: Iridium (`Ir`), atomic number 77.
Ir = GenericElement("Ir", "Iridium", 77, 192.217, "#175487")
#: Platinum (`Pt`), atomic number 78.
Pt = GenericElement("Pt", "Platinum", 78, 195.084, "#d0d0e0")
#: Gold (`Au`), atomic number 79.
Au = GenericElement("Au", "Gold", 79, 196.967, "#ffd123")
#: Mercury (`Hg`), atomic number 80.
Hg = GenericElement("Hg", "Mercury", 80, 200.59, "#b8b8d0")
#: Thallium (`Tl`), atomic number 81.
Tl = GenericElement("Tl", "Thallium", 81, 204.383, "#a6544d")
#: Lead (`Pb`), atomic number 82.
Pb = GenericElement("Pb", "Lead", 82, 207.2, "#575961")
#: Bismuth (`Bi`), atomic number 83.
Bi = GenericElement("Bi", "Bismuth", 83, 208.98, "#9e4fb5")
#: Polonium (`Po`), atomic number 84.
Po = GenericElement("Po", "Polonium", 84, 210.0, "#ab5c00")
#: Astatine (`At`), atomic number 85.
At = GenericElement("At", "Astatine", 85, 210.0, "#754f45")
#: Radon (`Rn`), atomic number 86.
Rn = GenericElement("Rn", "Radon", 86, 222.0, "#428296")
#: Francium (`Fr`), atomic number 87.
Fr = GenericElement("Fr", "Francium", 87, 223.0, "#420066")
#: Radium (`Ra`), atomic number 88.
Ra = GenericElement("Ra", "Radium", 88, 226.0, "#007d00")
#: Actinium (`Ac`), atomic number 89.
Ac = GenericElement("Ac", "Actinium", 89, 227.0, "#70abfa")
#: Thorium (`Th`), atomic number 90.
Th = GenericElement("Th", "Thorium", 90, 232.038, "#00baff")
#: Protactinium (`Pa`), atomic number 91.
Pa = GenericElement("Pa", "Protactinium", 91, 231.036, "#00a1ff")
#: Uranium (`U`), atomic number 92.
U = GenericElement("U", "Uranium", 92, 238.029, "#008fff")
#: Neptunium (`Np`), atomic number 93.
Np = GenericElement("Np", "Neptunium", 93, 237.0, "#0080ff")
#: Plutonium (`Pu`), atomic number 94.
Pu = GenericElement("Pu", "Plutonium", 94, 244.0, "#006bff")
#: Americium (`Am`), atomic number 95.
Am = GenericElement("Am", "Americium", 95, 243.0, "#545cf2")
#: Curium (`Cm`), atomic number 96.
Cm = GenericElement("Cm", "Curium", 96, 247.0, "#785ce3")
#: Berkelium (`Bk`), atomic number 97.
Bk = GenericElement("Bk", "Berkelium", 97, 247.0, "#8a4fe3")
#: Californium (`Cf`), atomic number 98.
Cf = GenericElement("Cf", "Californium", 98, 251.0, "#a136d4")
#: Einsteinium (`Es`), atomic number 99.
Es = GenericElement("Es", "Einsteinium", 99, 252.0, "#b31fd4")
#: Fermium (`Fm`), atomic number 100.
Fm = GenericElement("Fm", "Fermium", 100, 257.0, "#b31fba")
#: Mendelevium (`Md`), atomic number 101.
Md = GenericElement("Md", "Mendelevium", 101, 258.0, "#b30da6")
#: Nobelium (`No`), atomic number 102.
No = GenericElement("No", "Nobelium", 102, 259.0, "#bd0d87")
#: Lawrencium (`Lr`), atomic number 103.
Lr = GenericElement("Lr", "Lawrencium", 103, 262.0, "#c70066")
#: Rutherfordium (`Rf`), atomic number 104.
Rf = GenericElement("Rf", "Rutherfordium", 104, 261.0, "#cc0059")
#: Dubnium (`Db`), atomic number 105.
Db = GenericElement("Db", "Dubnium", 105, 262.0, "#d1004f")
#: Seaborgium (`Sg`), atomic number 106.
Sg = GenericElement("Sg", "Seaborgium", 106, 266.0, "#d90045")
#: Bohrium (`Bh`), atomic number 107.
Bh = GenericElement("Bh", "Bohrium", 107, 264.0, "#e00038")
#: Hassium (`Hs`), atomic number 108.
Hs = GenericElement("Hs", "Hassium", 108, 267.0, "#e6002e")
#: Meitnerium (`Mt`), atomic number 109.
Mt = GenericElement("Mt", "Meitnerium", 109, 268.0, "#eb0026")
#: Darmstadtium (`Ds`), atomic number 110.
Ds = GenericElement("Ds", "Darmstadtium", 110, 271.0, "#eb0026")
#: Roentgenium (`Rg`), atomic number 111.
Rg = GenericElement("Rg", "Roentgenium", 111, 272.0, "#eb0026")
#: Copernicium (`Cn`), atomic number 112.
Cn = GenericElement("Cn", "Copernicium", 112, 285.0, "#eb0026")
#: Nihonium (`Nh`), atomic number 113.
Nh = GenericElement("Nh", "Nihonium", 113, 284.0, "#eb0026")
#: Flerovium (`Fl`), atomic number 114.
Fl = GenericElement("Fl", "Flerovium", 114, 289.0, "#eb0026")
#: Moscovium (`Mc`), atomic number 115.
Mc = GenericElement("Mc", "Moscovium", 115, 288.0, "#eb0026")
#: Livermorium (`Lv`), atomic number 116.
Lv = GenericElement("Lv", "Livermorium", 116, 292.0, "#eb0026")
#: Tennessine (`Ts`), atomic number 117.
Ts = GenericElement("Ts", "Tennessine", 117, 295.0, "#eb0026")
#: Oganesson (`Og`), atomic number 118.
Og = GenericElement("Og", "Oganesson", 118, 294.0, "#eb0026")


# Generic Elements in Spanish
#: Hidrógeno (`H`), atomic number 1.
H_ESP = GenericElement("H", "Hidrógeno", 1, 1.007, "#ffffff")
#: Helio (`He`), atomic number 2.
He_ESP = GenericElement("He", "Helio", 2, 4.002, "#d9ffff")
#: Litio (`Li`), atomic number 3.
Li_ESP = GenericElement("Li", "Litio", 3, 6.941, "#cc80ff")
#: Berilio (`Be`), atomic number 4.
Be_ESP = GenericElement("Be", "Berilio", 4, 9.012, "#c2ff00")
#: Boro (`B`), atomic number 5.
B_ESP = GenericElement("B", "Boro", 5, 10.811, "#ffb5b5")
#: Carbono (`C`), atomic number 6.
C_ESP = GenericElement("C", "Carbono", 6, 12.011, "#909090")
#: Nitrógeno (`N`), atomic number 7.
N_ESP = GenericElement("N", "Nitrógeno", 7, 14.007, "#3050f8")
#: Oxígeno (`O`), atomic number 8.
O_ESP = GenericElement("O", "Oxígeno", 8, 15.999, "#ff0d0d")
#: Flúor (`F`), atomic number 9.
F_ESP = GenericElement("F", "Flúor", 9, 18.998, "#90e050")
#: Neón (`Ne`), atomic number 10.
Ne_ESP = GenericElement("Ne", "Neón", 10, 20.18, "#b3e3f5")
#: Sodio (`Na`), atomic number 11.
Na_ESP = GenericElement("Na", "Sodio", 11, 22.99, "#ab5cf2")
#: Magnesio (`Mg`), atomic number 12.
Mg_ESP = GenericElement("Mg", "Magnesio", 12, 24.305, "#8aff00")
#: Aluminio (`Al`), atomic number 13.
Al_ESP = GenericElement("Al", "Aluminio", 13, 26.982, "#bfa6a6")
#: Silicio (`Si`), atomic number 14.
Si_ESP = GenericElement("Si", "Silicio", 14, 28.086, "#f0c8a0")
#: Fósforo (`P`), atomic number 15.
P_ESP = GenericElement("P", "Fósforo", 15, 30.974, "#ff8000")
#: Azufre (`S`), atomic number 16.
S_ESP = GenericElement("S", "Azufre", 16, 32.065, "#ffff30")
#: Cloro (`Cl`), atomic number 17.
Cl_ESP = GenericElement("Cl", "Cloro", 17, 35.453, "#1ff01f")
#: Argón (`Ar`), atomic number 18.
Ar_ESP = GenericElement("Ar", "Argón", 18, 39.948, "#80d1e3")
#: Potasio (`K`), atomic number 19.
K_ESP = GenericElement("K", "Potasio", 19, 39.098, "#8f40d4")
#: Calcio (`Ca`), atomic number 20.
Ca_ESP = GenericElement("Ca", "Calcio", 20, 40.078, "#3dff00")
#: Escandio (`Sc`), atomic number 21.
Sc_ESP = GenericElement("Sc", "Escandio", 21, 44.956, "#e6e6e6")
#: Titanio (`Ti`), atomic number 22.
Ti_ESP = GenericElement("Ti", "Titanio", 22, 47.867, "#bfc2c7")
#: Vanadio (`V`), atomic number 23.
V_ESP = GenericElement("V", "Vanadio", 23, 50.942, "#a6a6ab")
#: Cromo (`Cr`), atomic number 24.
Cr_ESP = GenericElement("Cr", "Cromo", 24, 51.996, "#8a99c7")
#: Manganeso (`Mn`), atomic number 25.
Mn_ESP = GenericElement("Mn", "Manganeso", 25, 54.938, "#9c7ac7")
#: Hierro (`Fe`), atomic number 26.
Fe_ESP = GenericElement("Fe", "Hierro", 26, 55.845, "#e06633")
#: Cobalto (`Co`), atomic number 27.
Co_ESP = GenericElement("Co", "Cobalto", 27, 58.933, "#f090a0")
#: Níquel (`Ni`), atomic number 28.
Ni_ESP = GenericElement("Ni", "Níquel", 28, 58.693, "#50d050")
#: Cobre (`Cu`), atomic number 29.
Cu_ESP = GenericElement("Cu", "Cobre", 29, 63.546, "#c88033")
#: Zinc (`Zn`), atomic number 30.
Zn_ESP = GenericElement("Zn", "Zinc", 30, 65.38, "#7d80b0")
#: Galio (`Ga`), atomic number 31.
Ga_ESP = GenericElement("Ga", "Galio", 31, 69.723, "#c28f8f")
#: Germanio (`Ge`), atomic number 32.
Ge_ESP = GenericElement("Ge", "Germanio", 32, 72.64, "#668f8f")
#: Arsénico (`As`), atomic number 33.
As_ESP = GenericElement("As", "Arsénico", 33, 74.922, "#bd80e3")
#: Selenio (`Se`), atomic number 34.
Se_ESP = GenericElement("Se", "Selenio", 34, 78.96, "#ffa100")
#: Bromo (`Br`), atomic number 35.
Br_ESP = GenericElement("Br", "Bromo", 35, 79.904, "#a62929")
#: Kripton (`Kr`), atomic number 36.
Kr_ESP = GenericElement("Kr", "Kripton", 36, 83.798, "#5cb8d1")
#: Rubidio (`Rb`), atomic number 37.
Rb_ESP = GenericElement("Rb", "Rubidio", 37, 85.468, "#702eb0")
#: Estroncio (`Sr`), atomic number 38.
Sr_ESP = GenericElement("Sr", "Estroncio", 38, 87.62, "#00ff00")
#: Itrio (`Y`), atomic number 39.
Y_ESP = GenericElement("Y", "Itrio", 39, 88.906, "#94ffff")
#: Zirconio (`Zr`), atomic number 40.
Zr_ESP = GenericElement("Zr", "Zirconio", 40, 91.224, "#94e0e0")
#: Niobio (`Nb`), atomic number 41.
Nb_ESP = GenericElement("Nb", "Niobio", 41, 92.906, "#73c2c9")
#: Molybdeno (`Mo`), atomic number 42.
Mo_ESP = GenericElement("Mo", "Molybdeno", 42, 95.96, "#54b5b5")
#: Tecnecio (`Tc`), atomic number 43.
Tc_ESP = GenericElement("Tc", "Tecnecio", 43, 98.0, "#3b9e9e")
#: Rutenio (`Ru`), atomic number 44.
Ru_ESP = GenericElement("Ru", "Rutenio", 44, 101.07, "#248f8f")
#: Rodio (`Rh`), atomic number 45.
Rh_ESP = GenericElement("Rh", "Rodio", 45, 102.906, "#0a7d8c")
#: Paladio (`Pd`), atomic number 46.
Pd_ESP = GenericElement("Pd", "Paladio", 46, 106.42, "#006985")
#: Plata (`Ag`), atomic number 47.
Ag_ESP = GenericElement("Ag", "Plata", 47, 107.868, "#c0c0c0")
#: Cadmio (`Cd`), atomic number 48.
Cd_ESP = GenericElement("Cd", "Cadmio", 48, 112.411, "#ffd98f")
#: Indio (`In`), atomic number 49.
In_ESP = GenericElement("In", "Indio", 49, 114.818, "#a67573")
#: Estaño (`Sn`), atomic number 50.
Sn_ESP = GenericElement("Sn", "Estaño", 50, 118.71, "#668080")
#: Antimonio (`Sb`), atomic number 51.
Sb_ESP = GenericElement("Sb", "Antimonio", 51, 121.76, "#9e63b5")
#: Telurio (`Te`), atomic number 52.
Te_ESP = GenericElement("Te", "Telurio", 52, 127.6, "#d47a00")
#: Yodo (`I`), atomic number 53.
I_ESP = GenericElement("I", "Yodo", 53, 126.904, "#940094")
#: Xenón (`Xe`), atomic number 54.
Xe_ESP = GenericElement("Xe", "Xenón", 54, 131.293, "#429eb0")
#: Cesio (`Cs`), atomic number 55.
Cs_ESP = GenericElement("Cs", "Cesio", 55, 132.905, "#57178f")
#: Bario (`Ba`), atomic number 56.
Ba_ESP = GenericElement("Ba", "Bario", 56, 137.327, "#00c900")
#: Lantano (`La`), atomic number 57.
La_ESP = GenericElement("La", "Lantano", 57, 138.905, "#70d4ff")
#: Cerio (`Ce`), atomic number 58.
Ce_ESP = GenericElement("Ce", "Cerio", 58, 140.116, "#ffffc7")
#: Praseodimio (`Pr`), atomic number 59.
Pr_ESP = GenericElement("Pr", "Praseodimio", 59, 140.908, "#d9ffc7")
#: Neodimio (`Nd`), atomic number 60.
Nd_ESP = GenericElement("Nd", "Neodimio", 60, 144.242, "#c7ffc7")
#: Prometio (`Pm`), atomic number 61.
Pm_ESP = GenericElement("Pm", "Prometio", 61, 145.0, "#a3ffc7")
#: Samario (`Sm`), atomic number 62.
Sm_ESP = GenericElement("Sm", "Samario", 62, 150.36, "#8fffc7")
#: Europio (`Eu`), atomic number 63.
Eu_ESP = GenericElement("Eu", "Europio", 63, 151.964, "#61ffc7")
#: Gadolinio (`Gd`), atomic number 64.
Gd_ESP = GenericElement("Gd", "Gadolinio", 64, 157.25, "#45ffc7")
#: Terbio (`Tb`), atomic number 65.
Tb_ESP = GenericElement("Tb", "Terbio", 65, 158.925, "#30ffc7")
#: Disprosio (`Dy`), atomic number 66.
Dy_ESP = GenericElement("Dy", "Disprosio", 66, 162.5, "#1fffc7")
#: Holmio (`Ho`), atomic number 67.
Ho_ESP = GenericElement("Ho", "Holmio", 67, 164.93, "#00ff9c")
#: Erbio (`Er`), atomic number 68.
Er_ESP = GenericElement("Er", "Erbio", 68, 167.259, "#00e675")
#: Tulio (`Tm`), atomic number 69.
Tm_ESP = GenericElement("Tm", "Tulio", 69, 168.934, "#00d452")
#: Iterbio (`Yb`), atomic number 70.
Yb_ESP = GenericElement("Yb", "Iterbio", 70, 173.054, "#00bf38")
#: Lutecio (`Lu`), atomic number 71.
Lu_ESP = GenericElement("Lu", "Lutecio", 71, 174.967, "#00ab24")
#: Hafnio (`Hf`), atomic number 72.
Hf_ESP = GenericElement("Hf", "Hafnio", 72, 178.49, "#4dc2ff")
#: Tántalo (`Ta`), atomic number 73.
Ta_ESP = GenericElement("Ta", "Tántalo", 73, 180.948, "#4da6ff")
#: Wolframio (`W`), atomic number 74.
W_ESP = GenericElement("W", "Wolframio", 74, 183.84, "#2194d6")
#: Renio (`Re`), atomic number 75.
Re_ESP = GenericElement("Re", "Renio", 75, 186.207, "#267dab")
#: Osmio (`Os`), atomic number 76.
Os_ESP = GenericElement("Os", "Osmio", 76, 190.23, "#266696")
#: Iridio (`Ir`), atomic number 77.
Ir_ESP = GenericElement("Ir", "Iridio", 77, 192.217, "#175487")
#: Platino (`Pt`), atomic number 78.
Pt_ESP = GenericElement("Pt", "Platino", 78, 195.084, "#d0d0e0")
#: Oro (`Au`), atomic number 79.
Au_ESP = GenericElement("Au", "Oro", 79, 196.967, "#ffd123")
#: Mercurio (`Hg`), atomic number 80.
Hg_ESP = GenericElement("Hg", "Mercurio", 80, 200.59, "#b8b8d0")
#: Talio (`Tl`), atomic number 81.
Tl_ESP = GenericElement("Tl", "Talio", 81, 204.383, "#a6544d")
#: Plomo (`Pb`), atomic number 82.
Pb_ESP = GenericElement("Pb", "Plomo", 82, 207.2, "#575961")
#: Bismuto (`Bi`), atomic number 83.
Bi_ESP = GenericElement("Bi", "Bismuto", 83, 208.98, "#9e4fb5")
#: Polonio (`Po`), atomic number 84.
Po_ESP = GenericElement("Po", "Polonio", 84, 210.0, "#ab5c00")
#: Astato (`At`), atomic number 85.
At_ESP = GenericElement("At", "Astato", 85, 210.0, "#754f45")
#: Radón (`Rn`), atomic number 86.
Rn_ESP = GenericElement("Rn", "Radón", 86, 222.0, "#428296")
#: Francio (`Fr`), atomic number 87.
Fr_ESP = GenericElement("Fr", "Francio", 87, 223.0, "#420066")
#: Radio (`Ra`), atomic number 88.
Ra_ESP = GenericElement("Ra", "Radio", 88, 226.0, "#007d00")
#: Actinio (`Ac`), atomic number 89.
Ac_ESP = GenericElement("Ac", "Actinio", 89, 227.0, "#70abfa")
#: Torio (`Th`), atomic number 90.
Th_ESP = GenericElement("Th", "Torio", 90, 232.038, "#00baff")
#: Protactinio (`Pa`), atomic number 91.
Pa_ESP = GenericElement("Pa", "Protactinio", 91, 231.036, "#00a1ff")
#: Uranio (`U`), atomic number 92.
U_ESP = GenericElement("U", "Uranio", 92, 238.029, "#008fff")
#: Neptunio (`Np`), atomic number 93.
Np_ESP = GenericElement("Np", "Neptunio", 93, 237.0, "#0080ff")
#: Plutonio (`Pu`), atomic number 94.
Pu_ESP = GenericElement("Pu", "Plutonio", 94, 244.0, "#006bff")
#: Americio (`Am`), atomic number 95.
Am_ESP = GenericElement("Am", "Americio", 95, 243.0, "#545cf2")
#: Curio (`Cm`), atomic number 96.
Cm_ESP = GenericElement("Cm", "Curio", 96, 247.0, "#785ce3")
#: Berkelio (`Bk`), atomic number 97.
Bk_ESP = GenericElement("Bk", "Berkelio", 97, 247.0, "#8a4fe3")
#: Californio (`Cf`), atomic number 98.
Cf_ESP = GenericElement("Cf", "Californio", 98, 251.0, "#a136d4")
#: Einsteinio (`Es`), atomic number 99.
Es_ESP = GenericElement("Es", "Einsteinio", 99, 252.0, "#b31fd4")
#: Fermio (`Fm`), atomic number 100.
Fm_ESP = GenericElement("Fm", "Fermio", 100, 257.0, "#b31fba")
#: Mendelevio (`Md`), atomic number 101.
Md_ESP = GenericElement("Md", "Mendelevio", 101, 258.0, "#b30da6")
#: Nobelio (`No`), atomic number 102.
No_ESP = GenericElement("No", "Nobelio", 102, 259.0, "#bd0d87")
#: Lawrencio (`Lr`), atomic number 103.
Lr_ESP = GenericElement("Lr", "Lawrencio", 103, 262.0, "#c70066")
#: Rutherfordio (`Rf`), atomic number 104.
Rf_ESP = GenericElement("Rf", "Rutherfordio", 104, 261.0, "#cc0059")
#: Dubnio (`Db`), atomic number 105.
Db_ESP = GenericElement("Db", "Dubnio", 105, 262.0, "#d1004f")
#: Seaborgio (`Sg`), atomic number 106.
Sg_ESP = GenericElement("Sg", "Seaborgio", 106, 266.0, "#d90045")
#: Bohrio (`Bh`), atomic number 107.
Bh_ESP = GenericElement("Bh", "Bohrio", 107, 264.0, "#e00038")
#: Hassio (`Hs`), atomic number 108.
Hs_ESP = GenericElement("Hs", "Hassio", 108, 267.0, "#e6002e")
#: Meitnerio (`Mt`), atomic number 109.
Mt_ESP = GenericElement("Mt", "Meitnerio", 109, 268.0, "#eb0026")
#: Darmstadtio (`Ds`), atomic number 110.
Ds_ESP = GenericElement("Ds", "Darmstadtio", 110, 271.0, "#eb0026")
#: Roentgenio (`Rg`), atomic number 111.
Rg_ESP = GenericElement("Rg", "Roentgenio", 111, 272.0, "#eb0026")
#: Copernicio (`Cn`), atomic number 112.
Cn_ESP = GenericElement("Cn", "Copernicio", 112, 285.0, "#eb0026")
#: Nihonio (`Nh`), atomic number 113.
Nh_ESP = GenericElement("Nh", "Nihonio", 113, 284.0, "#eb0026")
#: Flerovio (`Fl`), atomic number 114.
Fl_ESP = GenericElement("Fl", "Flerovio", 114, 289.0, "#eb0026")
#: Moscovio (`Mc`), atomic number 115.
Mc_ESP = GenericElement("Mc", "Moscovio", 115, 288.0, "#eb0026")
#: Livermorio (`Lv`), atomic number 116.
Lv_ESP = GenericElement("Lv", "Livermorio", 116, 292.0, "#eb0026")
#: Teneso (`Ts`), atomic number 117.
Ts_ESP = GenericElement("Ts", "Teneso", 117, 295.0, "#eb0026")
#: Oganesón (`Og`), atomic number 118.
Og_ESP = GenericElement("Og", "Oganesón", 118, 294.0, "#eb0026")
