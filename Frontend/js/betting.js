// Het inzetbord: buiten-inzetten (rood/zwart/even/oneven) en de getallen 0-36.

import { BET_TYPES, colorOf } from "./config.js";

const OUTSIDE_BETS = ["red", "black", "even", "odd"];

export class BetBoard {
  constructor(container, onChange) {
    this.container = container;
    this.onChange = onChange;
    this.selection = null;
    this.buttons = [];
    this.render();
  }

  render() {
    const outside = document.createElement("div");
    outside.className = "outside-bets";
    for (const type of OUTSIDE_BETS) {
      outside.append(this.createButton({ type }, BET_TYPES[type].label, `bet-outside bet-${type}`));
    }

    const grid = document.createElement("div");
    grid.className = "number-grid";
    for (let n = 0; n <= 36; n++) {
      const cell = this.createButton({ type: "number", number: n }, String(n), `bet-number bet-${colorOf(n)}`);
      if (n === 0) {
        cell.classList.add("bet-zero");
      } else {
        // Bureaubladweergave: 12 kolommen x 3 rijen, mobiel: 3 kolommen x 12 rijen.
        const column = Math.ceil(n / 3);
        const row = 3 - ((n - 1) % 3);
        cell.style.setProperty("--desktop-col", column + 1);
        cell.style.setProperty("--desktop-row", row);
        cell.style.setProperty("--mobile-col", ((n - 1) % 3) + 1);
        cell.style.setProperty("--mobile-row", column + 1);
      }
      grid.append(cell);
    }

    this.container.replaceChildren(outside, grid);
  }

  createButton(bet, label, className) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.textContent = label;
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => this.select(bet, button));
    this.buttons.push(button);
    return button;
  }

  select(bet, button) {
    this.selection = bet;
    for (const b of this.buttons) b.setAttribute("aria-pressed", String(b === button));
    this.onChange(bet);
  }

  setDisabled(disabled) {
    for (const b of this.buttons) b.disabled = disabled;
  }
}
