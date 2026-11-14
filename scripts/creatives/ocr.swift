import Foundation
import Vision
import AppKit

// Usage : swift ocr.swift image1 [image2 ...]  → une ligne JSON par image {"file":…, "lines":[…]}
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("{\"file\":\"\(path)\",\"error\":\"illisible\"}")
        continue
    }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.recognitionLanguages = ["fr-FR"]
    req.usesLanguageCorrection = false
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    let lines = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }
    let obj: [String: Any] = ["file": path, "lines": lines]
    if let d = try? JSONSerialization.data(withJSONObject: obj, options: []), let s = String(data: d, encoding: .utf8) {
        print(s)
    }
}
