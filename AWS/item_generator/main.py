import utils
import asyncio
import time

start = time.time()
for _ in range(1):
    tasks = []
    for _ in range(20):
        random_keywords = utils.generate_keywords()
        random_libs = utils.generate_lib()
        tasks.append(utils.generate_item(user_search=random_keywords, selected_lib=random_libs))

    result = asyncio.run(asyncio.wait(tasks))
    time.sleep(0.7)
end = time.time()

print(f"총 {end-start} 소요")
