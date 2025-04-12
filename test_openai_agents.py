
try:
    from agents import Agent
    #Runner, handoff
    print("✅ SDK oficial 'openai.agents' instalado corretamente!")
except ImportError as e:
    print("❌ ERRO: Não foi possível importar 'openai.agents'")
    print("Detalhes:", e)
