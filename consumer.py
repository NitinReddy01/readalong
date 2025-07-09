# import json
# import asyncio
# import aio_pika
# import lambdaSpeechToScore  # Your existing scoring logic
# import logging
# from datetime import datetime
# import os

# QUEUE_NAME = "pronunciation_jobs"
# RABBITMQ_URL = "amqp://be-dev-services.eksaq.in/"  # Or get from env variable
# os.makedirs("logs", exist_ok=True)

# # Setup logger
# # Manual logger setup (doesn't rely on basicConfig)
# logger = logging.getLogger("PronunciationJobLogger")
# logger.setLevel(logging.INFO)

# # Create file handler
# file_handler = logging.FileHandler("logs/pronunciation_jobs.log")
# file_handler.setLevel(logging.INFO)

# # Formatter
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)

# # Add handler if not already added
# if not logger.hasHandlers():
#     logger.addHandler(file_handler)


# async def process_job(message: aio_pika.IncomingMessage):
#     async with message.process():
#         try:
#             raw_body = message.body.decode()
#             job_data = json.loads(raw_body)
#             job_id = job_data.get("jobId", "unknown")

#             if not all(k in job_data for k in ("base64Audio", "language", "title")):
#                 raise ValueError(f"Missing required fields in job: {job_data}")

#             start_time = datetime.now()
#             with open("logs/pronunciation_job_log.txt", "a") as f:
#                 f.write(f"\n[START] JobID: {job_id} at {start_time}\n")

#             event = {'body': json.dumps(job_data)}
#             output = await lambdaSpeechToScore.lambda_handler(event, [])

#             end_time = datetime.now()
#             with open("logs/pronunciation_job_log.txt", "a") as f:
#                 f.write(f"[END] JobID: {job_id} at {end_time}\n")
#                 f.write(f"[TIME] JobID: {job_id} at {end_time-start_time}\n")
#                 # f.write(f"[OUTPUT] JobID: {job_id} Output: {json.dumps(output)}\n")

#             print(f"[✓] Job {job_id} processed.")
#             message.ack()  # Acknowledge the message after processing

#         except Exception as e:
#             with open("logs/pronunciation_job_log.txt", "a") as f:
#                 f.write(f"[✗ ERROR] JobID: {job_data.get('jobId', 'unknown')}, Error: {str(e)}\n")
#             print(f"[✗] Failed to process job: {e}")



# CONCURRENCY = 5  # Number of concurrent consumers

# async def main():
#     connection = await aio_pika.connect_robust(RABBITMQ_URL)
#     channel = await connection.channel()
#     await channel.set_qos(prefetch_count=CONCURRENCY)

#     queue = await channel.declare_queue(QUEUE_NAME, durable=True)

#     print(f" [*] Waiting for jobs in '{QUEUE_NAME}' with {CONCURRENCY} workers. To exit press CTRL+C")

#     async def worker():
#         await queue.consume(process_job, no_ack=False)

#     # Spawn multiple worker tasks
#     workers = [asyncio.create_task(worker()) for _ in range(CONCURRENCY)]

#     await asyncio.gather(*workers)
    
#     await asyncio.Future()


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print(" [x] Gracefully shutting down.")
#     except Exception as e:
#         print(" [!] Unexpected error:", e)





import json
import asyncio
import aio_pika
import lambdaSpeechToScore  # Your existing scoring logic
import logging
from datetime import datetime
import os
import threading

QUEUE_NAME = "pronunciation_jobs"
RABBITMQ_URL = "amqp://be-dev-services.eksaq.in/"  # Or get from env variable
os.makedirs("logs", exist_ok=True)

# Setup logger
logger = logging.getLogger("PronunciationJobLogger")
logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler("logs/pronunciation_jobs.log")
file_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler if not already added
if not logger.hasHandlers():
    logger.addHandler(file_handler)

# Thread-safe counter for active workers
active_workers = threading.Lock()
active_count = 0

def log_worker_activity(worker_id, job_id, action, extra_info=""):
    """Thread-safe logging of worker activity"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_message = f"[{timestamp}] Worker-{worker_id} | JobID: {job_id} | {action}"
    if extra_info:
        log_message += f" | {extra_info}"
    
    with open("logs/pronunciation_job_log.txt", "a") as f:
        f.write(f"{log_message}\n")
    
    print(log_message)

async def process_job(message: aio_pika.IncomingMessage, worker_id: int):
    global active_count
    
    async with message.process():
        try:
            # Track active workers
            with active_workers:
                active_count += 1
                current_active = active_count
            
            raw_body = message.body.decode()
            job_data = json.loads(raw_body)
            job_id = job_data.get("jobId", "unknown")

            log_worker_activity(worker_id, job_id, "STARTED", f"Active workers: {current_active}")

            if not all(k in job_data for k in ("base64Audio", "language", "title")):
                raise ValueError(f"Missing required fields in job: {job_data}")

            start_time = datetime.now()
            
            log_worker_activity(worker_id, job_id, "PROCESSING", f"Started at {start_time.strftime('%H:%M:%S')}")

            # Your existing processing logic
            event = {'body': json.dumps(job_data)}
            output = await lambdaSpeechToScore.lambda_handler(event, [])

            end_time = datetime.now()
            processing_time = end_time - start_time
            
            log_worker_activity(worker_id, job_id, "COMPLETED", f"Duration: {processing_time.total_seconds():.2f}s")

          

        except Exception as e:
            log_worker_activity(worker_id, job_id if 'job_id' in locals() else "unknown", "ERROR", str(e))
            # Don't ack on error - let RabbitMQ retry
            message.nack(requeue=True)
        
        finally:
            # Decrement active worker count
            with active_workers:
                active_count -= 1
                remaining_active = active_count
            
            log_worker_activity(worker_id, job_id if 'job_id' in locals() else "unknown", "FINISHED", f"Active workers: {remaining_active}")

CONCURRENCY = 50  # Number of concurrent consumers

async def main():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    print(f" [*] Starting {CONCURRENCY} concurrent workers for queue '{QUEUE_NAME}'")
    print(f" [*] Waiting for jobs... To exit press CTRL+C")
    
    # Initialize log file with startup info
    with open("logs/pronunciation_job_log.txt", "a") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"[STARTUP] {datetime.now()} - Started {CONCURRENCY} workers\n")
        f.write(f"{'='*50}\n")

    async def worker(worker_id: int):
        print(f" [*] Worker-{worker_id} ready and waiting for jobs")
        
        async def job_callback(message):
            await process_job(message, worker_id)
        
        await queue.consume(job_callback, no_ack=False)

    # Spawn multiple worker tasks with unique IDs
    workers = [asyncio.create_task(worker(i+1)) for i in range(CONCURRENCY)]

    
    try:
        await asyncio.gather(*workers)
        await asyncio.Future()
    except Exception as e:
        print(f" [!] Error in workers: {e}")
        # Clean shutdown
        for worker in workers:
            worker.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(" [x] Gracefully shutting down...")
        with open("logs/pronunciation_job_log.txt", "a") as f:
            f.write(f"[SHUTDOWN] {datetime.now()} - Application stopped\n")
    except Exception as e:
        print(f" [!] Unexpected error: {e}")
        with open("logs/pronunciation_job_log.txt", "a") as f:
            f.write(f"[ERROR] {datetime.now()} - Unexpected error: {e}\n")
