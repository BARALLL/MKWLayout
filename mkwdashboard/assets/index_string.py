index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>MKW Telemetry Visualizer</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
            :root {
                --accent: #00f0ff;
                --accent-glow: rgba(0, 240, 255, 0.4);
                --glass-bg: rgba(20, 20, 20, 0.6);
                --glass-border: rgba(255, 255, 255, 0.1);
                --glass-hover: rgba(30, 30, 30, 0.8);
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Inter', sans-serif;
                background: #0f1115;
                min-height: 100vh;
                color: white;
                overflow-x: hidden;
            }

            /* Glass Panel Base */
            .glass-panel {
                background: var(--glass-bg);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid var(--glass-border);
                border-radius: 16px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .glass-panel:hover {
                background: var(--glass-hover);
            }

            /* Custom Dropdown Styling */
            .Select-control {
                background: var(--glass-bg) !important;
                border: 1px solid var(--glass-border) !important;
                border-radius: 12px !important;
                color: white !important;
            }

            .Select-menu-outer {
                background: var(--glass-bg) !important;
                backdrop-filter: blur(16px) !important;
                border: 1px solid var(--glass-border) !important;
                border-radius: 12px !important;
            }

            .Select-option {
                background: transparent !important;
                color: rgba(255, 255, 255, 0.7) !important;
            }

            .Select-option:hover {
                background: rgba(255, 255, 255, 0.1) !important;
                color: white !important;
            }

            .Select-option.is-selected {
                background: rgba(0, 240, 255, 0.2) !important;
                color: var(--accent) !important;
            }

            .Select-value-label {
                color: white !important;
            }

            .Select-placeholder {
                color: rgba(255, 255, 255, 0.5) !important;
            }

            /* Dash Dropdown Override */
            .dash-dropdown .Select-control {
                background: rgba(20, 20, 20, 0.8) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 10px !important;
                min-height: 42px !important;
            }

            .dash-dropdown .Select-value {
                color: white !important;
            }

            .dash-dropdown .Select-input input {
                color: white !important;
            }

            .dash-dropdown .Select-arrow {
                border-color: rgba(255, 255, 255, 0.5) transparent transparent !important;
            }

            .dash-dropdown .Select-menu-outer {
                background: rgba(20, 20, 20, 0.95) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 10px !important;
                margin-top: 4px !important;
                backdrop-filter: blur(16px) !important;
            }

            .dash-dropdown .VirtualizedSelectOption {
                background: transparent !important;
                color: rgba(255, 255, 255, 0.7) !important;
            }

            .dash-dropdown .VirtualizedSelectOption:hover {
                background: rgba(255, 255, 255, 0.1) !important;
                color: white !important;
            }

            .dash-dropdown .VirtualizedSelectFocusedOption {
                background: rgba(0, 240, 255, 0.15) !important;
                color: var(--accent) !important;
            }

            /* Custom Button Styling */
            .custom-button {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 12px 20px;
                background: linear-gradient(135deg, #1a56db, #1e40af);
                border: none;
                border-radius: 10px;
                color: white;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(26, 86, 219, 0.3);
            }

            .custom-button:hover {
                background: linear-gradient(135deg, #1e40af, #1a56db);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(26, 86, 219, 0.4);
            }

            .custom-button:active {
                transform: translateY(0);
            }

            .custom-button:disabled {
                background: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.3);
                cursor: not-allowed;
                box-shadow: none;
            }

            /* Secondary Button */
            .secondary-button {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                padding: 10px 16px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                color: rgba(255, 255, 255, 0.7);
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .secondary-button:hover {
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.2);
                color: white;
            }

            .secondary-button:disabled {
                opacity: 0.4;
                cursor: not-allowed;
            }

            /* Upload Button */
            .upload-button {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                padding: 14px 20px;
                background: rgba(0, 240, 255, 0.1);
                border: 1px dashed rgba(0, 240, 255, 0.4);
                border-radius: 12px;
                color: var(--accent);
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
            }

            .upload-button:hover {
                background: rgba(0, 240, 255, 0.15);
                border-color: var(--accent);
                box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
            }

            /* Slider Styling */
            .rc-slider {
                padding: 10px 0;
            }

            .rc-slider-rail {
                background: rgba(255, 255, 255, 0.1) !important;
                height: 4px !important;
                border-radius: 2px !important;
            }

            .rc-slider-track {
                background: linear-gradient(90deg, var(--accent), rgba(0, 240, 255, 0.6)) !important;
                height: 4px !important;
                border-radius: 2px !important;
            }

            .rc-slider-handle {
                background: var(--accent) !important;
                border: none !important;
                width: 16px !important;
                height: 16px !important;
                margin-top: -6px !important;
                box-shadow: 0 0 15px var(--accent-glow), 0 0 30px rgba(0, 240, 255, 0.2) !important;
                opacity: 1 !important;
            }

            .rc-slider-handle:hover {
                transform: scale(1.2);
            }

            .rc-slider-handle:active {
                box-shadow: 0 0 20px var(--accent-glow), 0 0 40px var(--accent-glow) !important;
            }

            .rc-slider-mark-text {
                color: rgba(255, 255, 255, 0.4) !important;
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 11px !important;
                display: inline-block;
                padding: 5px !important;
            }

            .rc-slider-tooltip-inner {
                background: rgba(0, 0, 0, 0.9) !important;
                border-radius: 6px !important;
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 11px !important;
                color: var(--accent) !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            }

            /* Checklist Styling */
            .custom-checklist label {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 16px;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 13px;
                color: rgba(255, 255, 255, 0.7);
            }

            .custom-checklist label:hover {
                background: rgba(255, 255, 255, 0.06);
                border-color: rgba(255, 255, 255, 0.15);
                color: white;
            }

            .custom-checklist input[type="checkbox"] {
                width: 18px;
                height: 18px;
                accent-color: var(--accent);
                cursor: pointer;
            }

            /* Labels */
            .label-text {
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.5);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 8px;
            }

            /* Section Headers */
            .section-header {
                font-family: 'Inter', sans-serif;
                font-size: 14px;
                font-weight: 600;
                color: white;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .section-header::before {
                content: '';
                width: 3px;
                height: 16px;
                background: var(--accent);
                border-radius: 2px;
            }

            /* Graph Container */
            .graph-container {
                background: rgba(15, 15, 20, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                overflow: hidden;
            }

            .js-plotly-plot .plotly .modebar {
                background: rgba(20, 20, 20, 0.8) !important;
                border-radius: 8px !important;
                padding: 4px !important;
            }

            .js-plotly-plot .plotly .modebar-btn {
                color: rgba(255, 255, 255, 0.6) !important;
            }

            .js-plotly-plot .plotly .modebar-btn:hover {
                color: var(--accent) !important;
            }

            /* File path display */
            .file-path-display {
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                color: rgba(255, 255, 255, 0.5);
                padding: 8px 12px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                margin-top: 10px;
                word-break: break-all;
            }

            /* Scrollbar */
            ::-webkit-scrollbar {
                width: 6px;
                height: 6px;
            }

            ::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 3px;
            }

            ::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: rgba(255, 255, 255, 0.3);
            }

            /* Animation */
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .fade-in-up {
                animation: fadeInUp 0.5s ease forwards;
            }

            .delay-1 { animation-delay: 0.1s; opacity: 0; }
            .delay-2 { animation-delay: 0.2s; opacity: 0; }
            .delay-3 { animation-delay: 0.3s; opacity: 0; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''