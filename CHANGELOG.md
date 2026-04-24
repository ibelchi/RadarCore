# Changelog - RadarCore

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-04-24
### Added
- **HTML Reporting**: New premium HTML report builder based on the Trazo design system.
- **English Localization**: Full-stack translation of UI, backend logs, and technical diagnostics.
- **Database Backfill**: Migration utility to fill missing RSI/Volume metrics in historical records.
- **Financial Disclaimer**: Legal notice added to all generated reports.
- **Market Sentiment Header**: Real-time macro indicators moved to the top of the History tab.

### Changed
- **Performance Defaults**: "Pre-filter universe" now ON by default.
- **UI Enhancements**: Risk-filtered opportunities are now expanded by default for better visibility.

---

## [1.1.0] - April 2026
### Added
- **Advanced Charting**: Integrated interactive TradingView charts for detailed price analysis.
- **Scan Diagnostics**: Implemented `ScanLogger` system providing feedback on why tickers were filtered (Liquidity, RSI, etc.).
- **Export Utilities**: Added PDF and Text export for sharing specific investment opportunities.
- **Universe Filtering**: Sidebar controls to toggle liquidity and "zombie stock" filters before scanning.
- **Watchlist Enhancements**: Added LinkColumns for direct access to Yahoo Finance from the table.

### Fixed
- **Chart Rendering**: Resolved "Black Chart" issue through robust timezone and datetime normalization.
- **Stability**: Fixed "Truth value of a Series is ambiguous" errors in the research module.
- **UI Sync**: Resolved widget key collisions when rendering multiple asset charts simultaneously.

---

## [1.0.0] - March 2026
### Added
- **Core Engine**: Initial release of the RadarCore Market Scanner with multi-strategy support.
- **Strategy Library**: Added Buy-the-Dip, High-Base Breakout, and Rebound strategies.
- **Persistence**: SQLite database integration for opportunity history and strategy configurations.
- **Authentication**: Implemented session-based password protection for cloud deployments.
- **AI Integration**: RAG engine for technical analysis explanations using Google Gemini.

---
*RadarCore: Advanced Swing Trading Intelligence*
