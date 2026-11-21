var builder = WebApplication.CreateBuilder(args);

var aiUrl = builder.Configuration["AI_BASE"] ?? "http://localhost:8000";

builder.Services.AddCors(o => o.AddDefaultPolicy(p => p.WithOrigins("http://localhost:5173").AllowAnyHeader().AllowAnyMethod()));
builder.Services.AddHttpClient("ai", c =>
{
    c.BaseAddress = new Uri(aiUrl);
    c.Timeout = TimeSpan.FromSeconds(30);
});
builder.Services.AddHttpClient("ai-train", c =>
{
    c.BaseAddress = new Uri(aiUrl);
    c.Timeout = TimeSpan.FromMinutes(5);
});

var app = builder.Build();

app.UseCors();

app.MapPost("/api/AI/predict", async (PredictIn predict, IHttpClientFactory factory) =>
{
    return await Send(() => factory.CreateClient("ai").PostAsJsonAsync("/predict", predict));
});

app.MapPost("/api/AI/apartments", async (ApartmentIn apartment, IHttpClientFactory factory) =>
{
    var error = Check(apartment);
    if (error != null)
    {
        return Results.BadRequest(new { detail = error });
    }

    return await Send(() => factory.CreateClient("ai").PostAsJsonAsync("/apartments", apartment));
});

app.MapPost("/api/AI/apartments/import", async (IFormFile? file, IHttpClientFactory factory) =>
{
    if (file == null || file.Length == 0)
    {
        return Results.BadRequest(new { detail = "CSV fayli secilmeyib" });
    }

    if (!file.FileName.EndsWith(".csv", StringComparison.OrdinalIgnoreCase))
    {
        return Results.BadRequest(new { detail = "Yalniz .csv fayl qebul olunur" });
    }

    using var stream = file.OpenReadStream();
    using var content = new MultipartFormDataContent();
    content.Add(new StreamContent(stream), "file", file.FileName);

    return await Send(() => factory.CreateClient("ai").PostAsync("/apartments/import", content));
}).DisableAntiforgery();

app.MapPost("/api/AI/retrain", async (IHttpClientFactory factory) =>
{
    return await Send(() => factory.CreateClient("ai-train").PostAsync("/retrain", null));
});

app.Run("http://localhost:5000");

static string? Check(ApartmentIn a)
{
    if (a.Bedrooms == null || a.Bedrooms <= 0 || a.Bedrooms % 1 != 0) return "Bedrooms musbet tam eded olmalidir";
    if (a.Bathrooms == null || a.Bathrooms <= 0 || a.Bathrooms % 1 != 0) return "Bathrooms musbet tam eded olmalidir";
    if (a.Sqm == null || a.Sqm <= 0) return "Sqm musbet eded olmalidir";
    if (string.IsNullOrWhiteSpace(a.City)) return "City bos ola bilmez";
    if (a.PriceAZN == null || a.PriceAZN <= 0) return "PriceAZN musbet eded olmalidir";
    return null;
}

static async Task<IResult> Send(Func<Task<HttpResponseMessage>> call)
{
    try
    {
        var response = await call();
        var body = await response.Content.ReadAsStringAsync();
        return Results.Content(body, "application/json", statusCode: (int)response.StatusCode);
    }
    catch (HttpRequestException)
    {
        return Results.Json(new { detail = "AI servisi (FastAPI) elcatan deyil" }, statusCode: 503);
    }
    catch (TaskCanceledException)
    {
        return Results.Json(new { detail = "AI servisi vaxtinda cavab vermedi" }, statusCode: 504);
    }
}

public record PredictIn(double Bedrooms, double Bathrooms, double Sqm, string City);

public record ApartmentIn(double? Bedrooms, double? Bathrooms, double? Sqm, string? City, double? PriceAZN);
