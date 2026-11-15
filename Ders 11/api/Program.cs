using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(o => o.AddDefaultPolicy(p => p.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod()));
builder.Services.AddHttpClient("fastapi", c => c.BaseAddress = new Uri("http://localhost:8000"));

var app = builder.Build();

app.UseCors();

app.MapPost("/api/predict", async (HouseRequest house, IHttpClientFactory factory) =>
{
    var client = factory.CreateClient("fastapi");
    var response = await client.PostAsJsonAsync("/predict", house);

    if (!response.IsSuccessStatusCode)
    {
        return Results.StatusCode(502);
    }

    var result = await response.Content.ReadFromJsonAsync<PriceResponse>();
    return Results.Ok(result);
});

app.Run("http://localhost:5000");

public record HouseRequest(
    [property: JsonPropertyName("city")] string City,
    [property: JsonPropertyName("square_meters")] double SquareMeters,
    [property: JsonPropertyName("bedrooms")] int Bedrooms,
    [property: JsonPropertyName("bathrooms")] int Bathrooms);

public record PriceResponse(
    [property: JsonPropertyName("price")] double Price);
