// Startpunt van de frontend: koppelt de API aan het wiel, het inzetbord en de weergave.

import { CONFIG } from "./config.js";
import { api } from "./api.js";
import { Wheel } from "./wheel.js";
import { BetBoard } from "./betting.js";
import { StatsView, ShopView, HistoryView, ResultView, Toast, formatMoney, formatTime } from "./ui.js";

class Game {
  constructor() {
    this.state = null;
    this.spinning = false;
    this.refreshing = false;

    this.el = {
      spinButton: document.getElementById("spin-button"),
      chips: document.getElementById("chip-row"),
      undoButton: document.getElementById("undo-button"),
      doubleButton: document.getElementById("double-button"),
      clearButton: document.getElementById("clear-button"),
      summary: document.getElementById("bet-summary"),
      saveButton: document.getElementById("save-button"),
      saveStatus: document.getElementById("save-status"),
      banner: document.getElementById("connection-banner"),
      bankrupt: document.getElementById("bankrupt-dialog"),
      resetButton: document.getElementById("reset-button"),
    };

    this.wheel = new Wheel(document.getElementById("wheel"), CONFIG.spinDurationMs);
    this.board = new BetBoard(document.getElementById("bet-board"), {
      onChange: () => this.updateControls(),
      canPlace: (extra) => this.canPlace(extra),
    });
    this.stats = new StatsView();
    this.shop = new ShopView(document.getElementById("shop-list"), (id) => this.buyUpgrade(id));
    this.history = new HistoryView(document.getElementById("history-list"));
    this.result = new ResultView(document.getElementById("last-result"));
    this.toast = new Toast(document.getElementById("toast"));
  }

  async start() {
    this.renderChips();
    this.selectChip(CONFIG.defaultChip);
    this.el.undoButton.addEventListener("click", () => this.board.undo());
    this.el.doubleButton.addEventListener("click", () => this.board.double());
    this.el.clearButton.addEventListener("click", () => this.board.clear());
    this.el.spinButton.addEventListener("click", () => this.spin());
    this.el.saveButton.addEventListener("click", () => this.save());
    this.el.resetButton.addEventListener("click", () => this.reset());
    // Blut is geen keuze: Escape mag de pop-up niet wegklikken.
    this.el.bankrupt.addEventListener("cancel", (event) => event.preventDefault());
    window.addEventListener("pagehide", () => api.saveOnExit());

    await this.refresh();
    const lastPlayerSpin = this.state?.history.find((spin) => spin.source === "player");
    this.result.show(lastPlayerSpin ?? null);

    setInterval(() => this.refresh(), CONFIG.pollIntervalMs);
    setInterval(() => this.save({ silent: true }), CONFIG.autoSaveIntervalMs);
  }

  renderChips() {
    const chips = CONFIG.chips.map(({ value, color, ink = "#fff" }) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip";
      chip.dataset.value = value;
      chip.style.setProperty("--chip-color", color);
      chip.style.setProperty("--chip-ink", ink);
      chip.textContent = value;
      chip.setAttribute("aria-label", `Fiche van ${formatMoney(value)}`);
      chip.addEventListener("click", () => this.selectChip(value));
      return chip;
    });
    this.el.chips.replaceChildren(...chips);
  }

  selectChip(value) {
    this.board.setChip(value);
    for (const chip of this.el.chips.children) {
      chip.setAttribute("aria-pressed", String(Number(chip.dataset.value) === value));
    }
  }

  canPlace(extra) {
    const balance = this.state?.balance ?? 0;
    if (this.board.total() + extra <= balance) return true;
    this.toast.show(`Onvoldoende saldo: je hebt ${formatMoney(balance)}.`, "error");
    return false;
  }

  updateControls() {
    const total = this.board.total();
    const balance = this.state?.balance ?? 0;
    let problem = null;

    if (this.state?.bankrupt) problem = "Je bent blut. Begin opnieuw om verder te spelen.";
    else if (total === 0) problem = "Kies een fiche en klik op de vakken waar je op wilt inzetten.";
    else if (total > balance) problem = `Onvoldoende saldo: je zet ${formatMoney(total)} in maar hebt ${formatMoney(balance)}.`;

    const spots = this.board.count === 1 ? "1 vak" : `${this.board.count} vakken`;
    this.el.summary.textContent = problem ?? `Totale inzet: ${formatMoney(total)} op ${spots}`;
    this.el.summary.classList.toggle("warning", total > 0 && Boolean(problem));

    this.el.spinButton.disabled = Boolean(problem) || this.spinning || !this.state;
    this.el.undoButton.disabled = this.spinning || !this.board.canUndo;
    this.el.doubleButton.disabled = this.spinning || total === 0;
    this.el.clearButton.disabled = this.spinning || total === 0;
    this.board.setDisabled(this.spinning);
  }

  applyState(state) {
    this.state = state;
    this.stats.render(state);
    this.shop.render(state.upgrades, state.balance);
    this.history.render(state.history);
    this.showBankrupt(state.bankrupt);
    this.updateControls();
  }

  showBankrupt(bankrupt) {
    const dialog = this.el.bankrupt;
    if (bankrupt && !dialog.open) dialog.showModal();
    else if (!bankrupt && dialog.open) dialog.close();
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
    const bets = this.board.getBets();
    if (bets.length === 0 || this.spinning) return;

    this.spinning = true;
    this.board.clearHighlights();
    this.updateControls();
    this.result.showSpinning();

    try {
      const { result, state } = await api.spin({ bets });
      await this.wheel.spinTo(result.number);
      this.result.show(result);
      // De inzetten blijven liggen, zodat je ze met één klik opnieuw kunt spelen.
      this.board.showResult(result);
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
      this.board.clear();
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
