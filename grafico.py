import matplotlib.pyplot as plt

# Datos de throughput
tecnologias = ["XML-RPC", "Pyro", "Redis", "RabbitMQ"]
single_node = [51.37, 49.30, 975.12, 3678.22]
escalado_estatico = [107.78, 53.12, 692.81, 3092.05]
escalado_dinamico = [758.78, 87.68, 143.33, 6193.96]

# Anchura de cada barra
bar_width = 0.25
x = range(len(tecnologias))

# Crear gráfico
plt.figure(figsize=(10, 6))
plt.bar(x, single_node, width=bar_width, label='Single-node')
plt.bar([i + bar_width for i in x], escalado_estatico, width=bar_width, label='Escalado estático')
plt.bar([i + 2*bar_width for i in x], escalado_dinamico, width=bar_width, label='Escalado dinámico')

# Configurar ejes y leyenda
plt.xlabel("Tecnología")
plt.ylabel("Throughput (req/s)")
plt.title("Comparación de rendimiento por middleware")
plt.xticks([i + bar_width for i in x], tecnologias)
plt.legend()
plt.tight_layout()

# Guardar imagen
plt.savefig("grafica_comparativa.png")
plt.show()  # Muestra la gráfica en una ventana
