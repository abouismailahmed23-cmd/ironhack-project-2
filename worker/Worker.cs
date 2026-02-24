using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Npgsql;
using StackExchange.Redis;

namespace Worker;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private IConnectionMultiplexer? _redis;
    private string _connectionString = "";
    private bool _isInitialized = false;

    public Worker(ILogger<Worker> logger)
    {
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Worker service starting...");

        try
        {
            // Initialize Redis connection
            var redisHost = Environment.GetEnvironmentVariable("REDIS_HOST") ?? "redis";
            var redisPort = Environment.GetEnvironmentVariable("REDIS_PORT") ?? "6379";
            
            _redis = ConnectionMultiplexer.Connect($"{redisHost}:{redisPort}");
            _logger.LogInformation("Connected to Redis at {Host}:{Port}", redisHost, redisPort);
            
            // Initialize PostgreSQL connection string
            var pgHost = Environment.GetEnvironmentVariable("PG_HOST") ?? "postgres";
            var pgPort = Environment.GetEnvironmentVariable("PG_PORT") ?? "5432";
            var pgUser = Environment.GetEnvironmentVariable("PG_USER") ?? "postgres";
            var pgPassword = Environment.GetEnvironmentVariable("PG_PASSWORD") ?? "postgres";
            var pgDatabase = Environment.GetEnvironmentVariable("PG_DATABASE") ?? "votes";
            
            _connectionString = $"Host={pgHost};Port={pgPort};Username={pgUser};Password={pgPassword};Database={pgDatabase}";
            
            // Create database table if not exists
            using (var connection = new NpgsqlConnection(_connectionString))
            {
                await connection.OpenAsync();
                
                var createTableCmd = @"
                    CREATE TABLE IF NOT EXISTS votes (
                        id SERIAL PRIMARY KEY,
                        vote TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )";
                
                using var cmd = new NpgsqlCommand(createTableCmd, connection);
                await cmd.ExecuteNonQueryAsync();
                
                _logger.LogInformation("Database table verified/created");
            }
            
            _isInitialized = true;
            
            // Subscribe to Redis channel
            var subscriber = _redis.GetSubscriber();
            _logger.LogInformation("Subscribing to Redis channel 'vote_channel'");

            await subscriber.SubscribeAsync("vote_channel", async (channel, vote) =>
            {
                if (!_isInitialized) return;
                
                _logger.LogInformation("Received vote: {Vote}", vote);
                
                try
                {
                    using var insertConnection = new NpgsqlConnection(_connectionString);
                    await insertConnection.OpenAsync();
                    
                    using var insertCmd = new NpgsqlCommand(
                        "INSERT INTO votes (vote) VALUES (@vote)", insertConnection);
                    insertCmd.Parameters.AddWithValue("vote", vote.ToString());
                    await insertCmd.ExecuteNonQueryAsync();
                    
                    _logger.LogInformation("Vote saved to database");
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error saving vote to database");
                }
            });

            // Keep the worker running
            while (!stoppingToken.IsCancellationRequested)
            {
                await Task.Delay(1000, stoppingToken);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Worker failed to start");
            throw;
        }
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Worker service stopping...");
        _isInitialized = false;
        
        if (_redis != null)
        {
            await _redis.CloseAsync();
        }
        
        await base.StopAsync(cancellationToken);
    }
}
