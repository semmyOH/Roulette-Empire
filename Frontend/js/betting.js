// Het inzetbord: getallen, straten, dozijnen, kolommen ("2 to 1") en rood/zwart/even/oneven.
// Elke klik legt de gekozen fiche op een vak. Je kunt op zoveel vakken inzetten als je wilt.

import { BET_TYPES, colorOf } from "./config.js";

const OUTSIDE_BETS = ["even", "red", "black", "odd"];
const DOZEN_LABELS = ["1e 12", "2e 12", "3e 12"];
const MAX_UNDO = 100;

export const betKey = (bet) => `${bet.bet_type}:${bet.value ?? ""}`;

function formatChipAmount(amount) {
  return amount >= 1000 ? `${Math.round(amount / 100) / 10}k` : String(amount);
}

export class BetBoard {
  /**
   * @param onChange  wordt aangeroepen na elke wijziging van de inzetten
   * @param canPlace  (extraBedrag) => boolean, bijvoorbeeld om het saldo te controleren
   */
  constructor(container, { onChange, canPlace }) {
    this.container = container;
    this.onChange = onChange;
    this.canPlace = canPlace;
    this.chipValue = 0;
    this.bets = new Map(); // sleutel -> { bet_type, value, amount }
    this.history = []; // eerdere versies van `bets`, voor "ongedaan maken"
    this.spots = new Map(); // sleutel -> { button, badge }
    this.render();
  }

  // Opbouw

  render() {
    const grid = document.createElement("div");
    grid.className = "table-grid";

    // Posities als [kolom, rij, kolombreedte, rijhoogte]: bureaublad liggend, mobiel staand.
    grid.append(this.createSpot({ bet_type: "number", value: 0 }, "0", "spot-number bet-green",
      { desktop: [1, 1, 1, 3], mobile: [2, 1, 3, 1] }));

    for (let n = 1; n <= 36; n++) {
      const column = Math.ceil(n / 3);
      const row = 3 - ((n - 1) % 3);
      grid.append(this.createSpot({ bet_type: "number", value: n }, String(n), `spot-number bet-${colorOf(n)}`,
        { desktop: [column + 1, row, 1, 1], mobile: [((n - 1) % 3) + 2, column + 1, 1, 1] }));
    }

    for (let s = 1; s <= 12; s++) {
      const label = `${3 * s - 2}-${3 * s}`;
      grid.append(this.createSpot({ bet_type: "street", value: s }, label, "spot-street",
        { desktop: [s + 1, 4, 1, 1], mobile: [5, s + 1, 1, 1] }, `Straat ${3 * s - 2}, ${3 * s - 1}, ${3 * s}`));
    }

    for (let c = 1; c <= 3; c++) {
      grid.append(this.createSpot({ bet_type: "column", value: c }, "2 to 1", "spot-column",
        { desktop: [14, 4 - c, 1, 1], mobile: [c + 1, 14, 1, 1] }, `Kolom ${c}`));
    }

    for (let d = 1; d <= 3; d++) {
      grid.append(this.createSpot({ bet_type: "dozen", value: d }, DOZEN_LABELS[d - 1], "spot-dozen",
        { desktop: [4 * d - 2, 5, 4, 1], mobile: [1, 4 * d - 2, 1, 4] }, `${DOZEN_LABELS[d - 1]} (${12 * d - 11}-${12 * d})`));
    }

    const outside = document.createElement("div");
    outside.className = "outside-bets";
    for (const type of OUTSIDE_BETS) {
      outside.append(this.createSpot({ bet_type: type, value: null }, BET_TYPES[type].label, `spot-outside bet-${type}`));
    }

    this.container.replaceChildren(grid, outside);
  }

  createSpot(bet, label, className, position, name = null) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `spot ${className}`;
    button.title = `${name ?? label} · ${BET_TYPES[bet.bet_type].payout}`;
    button.innerHTML = `<span class="spot-label"></span><span class="spot-chip" hidden></span>`;
    button.querySelector(".spot-label").textContent = label;

    if (position) {
      const [dc, dr, dcs, drs] = position.desktop;
      const [mc, mr, mcs, mrs] = position.mobile;
      const vars = { dc, dr, dcs, drs, mc, mr, mcs, mrs };
      for (const [prop, value] of Object.entries(vars)) button.style.setProperty(`--${prop}`, value);
    }

    const key = betKey(bet);
    button.addEventListener("click", () => this.add(bet));
    this.spots.set(key, { button, badge: button.querySelector(".spot-chip"), name: name ?? label });
    this.updateSpot(key);
    return button;
  }

  // Inzetten

  setChip(value) {
    this.chipValue = value;
  }

  add(bet) {
    if (!this.chipValue || !this.canPlace(this.chipValue)) return;
    this.remember();
    const key = betKey(bet);
    const current = this.bets.get(key);
    this.bets.set(key, { ...bet, amount: (current?.amount ?? 0) + this.chipValue });
    this.changed([key]);
  }

  double() {
    if (this.bets.size === 0 || !this.canPlace(this.total())) return;
    this.remember();
    for (const bet of this.bets.values()) bet.amount *= 2;
    this.changed([...this.bets.keys()]);
  }

  undo() {
    const previous = this.history.pop();
    if (!previous) return;
    const keys = new Set([...this.bets.keys(), ...previous.keys()]);
    this.bets = previous;
    this.changed([...keys]);
  }

  clear() {
    if (this.bets.size === 0) return;
    this.remember();
    const keys = [...this.bets.keys()];
    this.bets.clear();
    this.changed(keys);
  }

  getBets() {
    return [...this.bets.values()].map(({ bet_type, value, amount }) =>
      (value == null ? { bet_type, amount } : { bet_type, value, amount }));
  }

  total() {
    let total = 0;
    for (const bet of this.bets.values()) total += bet.amount;
    return total;
  }

  get count() {
    return this.bets.size;
  }

  get canUndo() {
    return this.history.length > 0;
  }

  remember() {
    this.history.push(new Map([...this.bets].map(([key, bet]) => [key, { ...bet }])));
    if (this.history.length > MAX_UNDO) this.history.shift();
  }

  changed(keys) {
    this.clearHighlights();
    for (const key of keys) this.updateSpot(key);
    this.onChange();
  }

  updateSpot(key) {
    const spot = this.spots.get(key);
    const amount = this.bets.get(key)?.amount ?? 0;
    spot.badge.hidden = amount === 0;
    spot.badge.textContent = formatChipAmount(amount);
    spot.button.classList.toggle("has-bet", amount > 0);
    spot.button.setAttribute("aria-label", amount > 0 ? `${spot.name}, inzet €${amount}` : spot.name);
  }

  // Resultaat

  showResult(result) {
    this.clearHighlights();
    this.spots.get(betKey({ bet_type: "number", value: result.number }))?.button.classList.add("hit");
    for (const bet of result.bets ?? []) {
      if (bet.net > 0) this.spots.get(betKey(bet))?.button.classList.add("won");
    }
  }

  clearHighlights() {
    for (const { button } of this.spots.values()) button.classList.remove("hit", "won");
  }

  setDisabled(disabled) {
    for (const { button } of this.spots.values()) button.disabled = disabled;
  }
}
