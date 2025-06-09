mkdir -p ~/.streamlit/
echo "\n[server]\nheadless = true\nport = $PORT\nenableCORS = false\n\n[browser]\ngatherUsageStats = false\n" > ~/.streamlit/config.toml
