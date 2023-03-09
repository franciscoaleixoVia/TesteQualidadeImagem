
using System.Net.Http.Handlers;
using System.Security.Cryptography;

Console.WriteLine("Execute: C:>TesteClient '*.jpg'");

foreach (string file in ExpandFilePaths(args))
{
    Upload("http://127.0.0.1:88/check_image", file);

    // Console.WriteLine($"\nProcessado arquivo {file} Resultado: {resultado}");
}

Console.WriteLine("Fim do Processamento!");

async void Upload(string url, string filename)
{
    var stream = File.OpenRead(filename);
    HttpContent fileStreamContent = new StreamContent(stream);

    using (var handler = new ProgressMessageHandler())
    using (var client = HttpClientFactory.Create(handler))
    using (var formData = new MultipartFormDataContent())
    {
        client.Timeout = new TimeSpan(1, 0, 0); // 1 hour should be enough probably

        formData.Add(fileStreamContent, "image", filename);

        handler.HttpSendProgress += (s, e) =>
        {
            float prog = (float)e.BytesTransferred / (float)stream.Length;
            prog = prog > 1 ? 1 : prog;
            Console.Write($"\r({filename}--> {prog.ToString()} ");
        };

        var response_raw = client.PostAsync(url, formData);

        var response = response_raw.Result;

        if (response.IsSuccessStatusCode)
        {

            Console.WriteLine($"Resultado: {await response.Content.ReadAsStringAsync()}");

        }
    }
}

static string[] ExpandFilePaths(string[] args)
{
    var fileList = new List<string>();

    foreach (var arg in args)
    {
        var substitutedArg = System.Environment.ExpandEnvironmentVariables(arg);

        var dirPart = Path.GetDirectoryName(substitutedArg);
        if (dirPart.Length == 0)
            dirPart = ".";

        var filePart = Path.GetFileName(substitutedArg);

        foreach (var filepath in Directory.GetFiles(dirPart, filePart))
            fileList.Add(filepath);
    }

    return fileList.ToArray();
}


