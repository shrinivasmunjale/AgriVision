import imageCompression from 'browser-image-compression'

/**
 * Checks image dimensions without decoding the full bitmap into memory for long.
 * @param {File} file 
 * @returns {Promise<{width: number, height: number}>}
 */
const getImageDimensions = (file) => {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      URL.revokeObjectURL(url)
      resolve({ width: img.naturalWidth || img.width, height: img.naturalHeight || img.height })
    }
    img.onerror = (err) => {
      URL.revokeObjectURL(url)
      reject(err)
    }
    img.src = url
  })
}

/**
 * Default compression options optimized for YOLOv8 leaf detection & EfficientNet classification
 */
const DEFAULT_OPTIONS = {
  maxSizeMB: 1.0,           // Target under ~1MB (high quality)
  maxWidthOrHeight: 1600,   // Max 1600px width/height while maintaining aspect ratio
  useWebWorker: true,       // Non-blocking off-main-thread compression
  fileType: 'image/jpeg',   // Normalize all formats (PNG, HEIC, TIFF, WebP) to standard JPEG
  initialQuality: 0.8,      // 80% JPEG quality (visually lossless for plant disease detection)
  alwaysKeepResolution: false,
}

/**
 * Computes a short SHA-256 hash prefix of a File for diagnostic consistency tracking.
 * @param {File} file 
 * @returns {Promise<string>}
 */
const computeFileHash = async (file) => {
  try {
    const arrayBuffer = await file.arrayBuffer()
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('').slice(0, 16)
  } catch {
    return 'unavailable'
  }
}

/**
 * Compresses, reorients, and normalizes a single image file for AI leaf detection and disease analysis.
 * 
 * - Ensures all platforms (Android Chrome, iOS Safari, desktop) produce consistent, upright JPEG images.
 * - Bakes EXIF orientation into pixels via canvas processing.
 * - Normalizes output to standard JPEG at 80% quality.
 * - Returns a standard File object with preserved filename.
 * 
 * @param {File} file - Original File from input/camera
 * @param {Object} [customOptions] - Optional overrides
 * @returns {Promise<File>} Compressed and orientation-normalized File object ready for FormData
 */
export async function compressImage(file, customOptions = {}) {
  // If not an image file, return as-is
  if (!file || !file.type.startsWith('image/')) {
    return file
  }

  let origWidth = null
  let origHeight = null

  try {
    try {
      const dims = await getImageDimensions(file)
      origWidth = dims.width
      origHeight = dims.height
    } catch {
      // ignore dimension read failure
    }

    const options = {
      ...DEFAULT_OPTIONS,
      ...customOptions,
    }

    // Perform canvas resize + EXIF auto-rotation + standard JPEG encoding
    const compressedBlob = await imageCompression(file, options)

    // Ensure output file has .jpg / .jpeg extension
    const baseName = file.name.replace(/\.[^/.]+$/, '')
    const newFileName = `${baseName}.jpg`

    const processedFile = new File([compressedBlob], newFileName, {
      type: 'image/jpeg',
      lastModified: Date.now(),
    })

    // Diagnostic logging for cross-device consistency verification
    try {
      const processedDims = await getImageDimensions(processedFile)
      const processedHash = await computeFileHash(processedFile)
      console.log(
        `[IMG-DIAGNOSTIC-FRONTEND] Original: (${origWidth}x${origHeight}, ${(file.size / 1024).toFixed(1)}KB, ${file.type}) -> ` +
        `Processed: (${processedDims.width}x${processedDims.height}, ${(processedFile.size / 1024).toFixed(1)}KB, image/jpeg, hash16=${processedHash})`
      )
    } catch (logErr) {
      // Non-blocking diagnostic logging
    }

    // Return a standard File instance for direct FormData appending
    return processedFile
  } catch (error) {
    console.error(`Failed to compress/normalize image "${file.name}":`, error)
    // Fallback: return original file so the user upload does not fail
    return file
  }
}

/**
 * Compresses multiple images sequentially or in parallel batches with progress reporting.
 * 
 * @param {File[]} files - Array of File objects
 * @param {Object} [options]
 * @param {Function} [onProgress] - Callback (completedCount, totalCount) => void
 * @returns {Promise<File[]>} Array of compressed File objects
 */
export async function compressImages(files, options = {}, onProgress = null) {
  if (!files || files.length === 0) return []

  const total = files.length
  let completed = 0

  const compressedFiles = []

  for (const file of files) {
    const compressed = await compressImage(file, options)
    compressedFiles.push(compressed)
    completed += 1
    if (typeof onProgress === 'function') {
      onProgress(completed, total)
    }
  }

  return compressedFiles
}
