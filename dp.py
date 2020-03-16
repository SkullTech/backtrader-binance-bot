import random
from train_supertrend import evaluate
from deap import creator, base, tools, algorithms


creator.create('Fitness', base.Fitness, weights=(1.0, 1.0))
creator.create('Individual', list, fitness=creator.Fitness)

toolbox = base.Toolbox()

def initGene(icls):
    compression = random.uniform(15, 45)
    persistence = random.uniform(2, 10)
    period = random.uniform(5, 20)
    multiplier = random.uniform(1.2, 4)
    ind = icls([compression, persistence, period, multiplier])
    return ind

toolbox = base.Toolbox()
toolbox.register('individual', initGene, creator.Individual)
toolbox.register('population', tools.initRepeat, list, toolbox.individual)
toolbox.register('evaluate', evaluate)

toolbox.register('mate', tools.cxUniform, indpb=0.2)
toolbox.register('mutate', tools.mutGaussian, mu=0, sigma=(10, 3, 5, 1), indpb=0.2)
toolbox.register('select', tools.selBest)

population = toolbox.population(n=2)
print(population)
top5 = algorithms.eaMuPlusLambda(population, toolbox, mu=2, lambda_=2, cxpb=0.5, mutpb=0.2, ngen=5, verbose=True)
print(top5)

# NGEN=40
# for gen in range(NGEN):
#     offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
#     fits = toolbox.map(toolbox.evaluate, offspring)
#     for fit, ind in zip(fits, offspring):
#         ind.fitness.values = fit
#     population = toolbox.select(offspring, k=len(population))
# top10 = tools.selBest(population, k=10)

# print(top10)
