// Startpunt van de frontend: koppelt de API aan het wiel, het inzetbord en de weergave.

import { CONFIG, BET_TYPES } from "./config.js";
import { api } from "./api.js";
import { Wheel } from "./wheel.js";
import { BetBoard } from "./betting.js";
import { StatsView, ShopView, HistoryView, ResultView, Toast, formatMoney, formatTime } from "./ui.js";

class Game {
  constructor() {
    this.state = null;
    this.spinning = false;
    this.refreshing = false;
    this.maxBet = false;

    this.el = {
      spinButton: document.getElementById("spin-button"),
      amount: document.getElementById("bet-amount"),
      chips: document.getElementById("chip-row"),
      summary: document.getElementById("bet-summary"),
      saveButton: document.getElementById("save-button"),
      saveStatus: document.getElementById("save-status"),
      banner: document.getElementById("connection-banner"),
      bankrupt: document.getElementById("bankrupt-banner"),
      resetButton: document.getElementById("reset-button"),
    };

    this.wheel = new Wheel(document.getElementById("wheel"), CONFIG.spinDurationMs);
    this.board = new BetBoard(document.getElementById("bet-board"), () => this.updateControls());
    this.stats = new StatsView();
    this.shop = new ShopView(document.getElementById("shop-list"), (id) => this.buyUpgrade(id));
    this.history = new HistoryView(document.getElementById("history-list"));
    this.result = new ResultView(document.getElementById("last-result"));
    this.toast = new Toast(document.getElementById("toast"));
  }

  async start() {
    this.el.amount.value = CONFIG.defaultBet;
    this.renderChips();
    this.el.amount.addEventListener("input", () => {
      this.maxBet = false;
      this.updateControls();
    });
    this.el.spinButton.addEventListener("click", () => this.spin());
    this.el.saveButton.addEventListener("click", () => this.save());
    this.el.resetButton.addEventListener("click", () => this.reset());
    window.addEventListener("pagehide", () => api.saveOnExit());

    await this.refresh();
    const lastPlayerSpin = this.state?.history.find((spin) => spin.source === "player");
    this.result.show(lastPlayerSpin ?? null);

    setInterval(() => this.refresh(), CONFIG.pollIntervalMs);
    setInterval(() => this.save({ silent: true }), CONFIG.autoSaveIntervalMs);
  }

  renderChips() {
    const chips = CONFIG.chips.map((value) => this.createChip(formatMoney(value), () => value));
    chips.push(
      this.createChip("×2", () => this.betAmount() * 2),
      this.createChip("Max", () => this.maxAmount(), { max: true }),
    );
    this.el.chips.replaceChildren(...chips);
  }

  createChip(label, getValue, { max = false } = {}) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = label;
    chip.addEventListener("click", () => {
      this.maxBet = max;
      this.el.amount.value = Math.max(1, getValue());
      this.updateControls();
    });
    return chip;
  }

  // Bots veranderen het saldo; updateControls() houdt de Max-inzet daarom gelijk met het saldo.
  maxAmount() {
    if (!this.state) return 0;
    return Math.floor(this.state.balance);
  }

  betAmount() {
    return Math.floor(Number(this.el.amount.value)) || 0;
  }

  currentBet() {
    const selection = this.board.selection;
    if (!selection) return null;
    const bet = { bet_type: selection.type, amount: this.betAmount() };
    if (selection.type === "number") bet.number = selection.number;
    return bet;
  }

  describeBet(bet) {
    const target = bet.bet_type === "number" ? `getal ${bet.number}` : BET_TYPES[bet.bet_type].label;
    return `${formatMoney(bet.amount)} op ${target} (uitbetaling ${BET_TYPES[bet.bet_type].payout})`;
  }

  updateControls() {
    if (this.maxBet) this.el.amount.value = Math.max(1, this.maxAmount());
    const bet = this.currentBet();
    const balance = this.state?.balance ?? 0;
    let problem = null;

    if (this.state?.bankrupt) problem = "Je bent blut. Begin opnieuw om verder te spelen.";
    else if (!bet) problem = "Kies een vak op het bord.";
    else if (bet.amount < 1) problem = "Vul een inzet van minimaal €1 in.";
    else if (bet.amount > balance) problem = "Onvoldoende saldo voor deze inzet.";

    this.el.summary.textContent = problem ?? this.describeBet(bet);
    this.el.summary.classList.toggle("warning", Boolean(bet) && Boolean(problem));
    this.el.spinButton.disabled = Boolean(problem) || this.spinning || !this.state;
    this.board.setDisabled(this.spinning);
  }

  applyState(state) {
    this.state = state;
    this.stats.render(state);
    this.shop.render(state.upgrades, state.balance);
    this.history.render(state.history);
    this.el.bankrupt.hidden = !state.bankrupt;
    this.updateControls();
  }

  setConnected(connected) {
    this.el.banner.hidden = connected;
  }

  async refresh() {
    if (this.spinning || this.refreshing) return;
    this.refreshing = true;
    try {
      const state = await api.getState();
      // Een spin die tijdens het ophalen begon, mag niet overschreven worden door oudere data.
      if (!this.spinning) this.applyState(state);
      this.setConnected(true);
    } catch {
      this.setConnected(false);
    } finally {
      this.refreshing = false;
    }
  }

  async spin() {
    const bet = this.currentBet();
    if (!bet || this.spinning) return;

    this.spinning = true;
    this.updateControls();
    this.result.showSpinning();

    try {
      const { result, state } = await api.spin(bet);
      await this.wheel.spinTo(result.number);
      this.result.show(result);
      this.applyState(state);
    } catch (error) {
      this.result.restore();
      this.toast.show(error.message, "error");
    } finally {
      this.spinning = false;
      this.updateControls();
    }
  }

  async buyUpgrade(id) {
    try {
      const { state } = await api.buyUpgrade(id);
      const upgrade = state.upgrades.find((u) => u.id === id);
      this.applyState(state);
      this.toast.show(`${upgrade?.name ?? "Upgrade"} gekocht (niveau ${upgrade?.level}).`, "success");
    } catch (error) {
      this.toast.show(error.message, "error");
      if (this.state) this.shop.render(this.state.upgrades, this.state.balance);
    }
  }

  async reset() {
    this.el.resetButton.disabled = true;
    try {
      const { state } = await api.reset();
      this.maxBet = false;
      this.el.amount.value = CONFIG.defaultBet;
      this.result.show(null);
      this.applyState(state);
      this.toast.show("Nieuw begin: je hebt weer €100.", "success");
    } catch (error) {
      this.toast.show(error.message, "error");
    } finally {
      this.el.resetButton.disabled = false;
    }
  }

  async save({ silent = false } = {}) {
    try {
      const data = await api.save();
      const savedAt = data.saved_at ? new Date(data.saved_at) : new Date();
      this.el.saveStatus.textContent = `Opgeslagen om ${formatTime(savedAt)}`;
      if (!silent) this.toast.show("Voortgang opgeslagen.", "success");
    } catch (error) {
      this.el.saveStatus.textContent = "Opslaan mislukt";
      if (!silent) this.toast.show(error.message, "error");
    }
  }
}

new Game().start();
