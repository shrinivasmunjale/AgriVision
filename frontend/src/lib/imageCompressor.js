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
 * Compresses and resizes a single image file for AI leaf detection and disease analysis.
 * 
 * - Skips compression if image is already <= 1024x1024 AND < 500 KB.
 * - Maintains aspect ratio.
 * - Normalizes output to standard JPEG at 80% quality.
 * - Handles EXIF orientation automatically.
 * - Returns a standard File object with preserved filename.
 * 
 * @param {File} file - Original File from input/camera
 * @param {Object} [customOptions] - Optional overrides
 * @returns {Promise<File>} Compressed File object ready for FormData
 */
export async function compressImage(file, customOptions = {}) {
  // If not an image file, return as-is
  if (!file || !file.type.startsWith('image/')) {
    return file
  }

  try {
    // Condition: If image is <= 500KB and <= 1024x1024, pass through without recompressing
    const MAX_SKIP_BYTES = 500 * 1024 // 500 KB
    const MAX_SKIP_DIM = 1024         // 1024px

    if (file.size <= MAX_SKIP_BYTES) {
      try {
        const { width, height } = await getImageDimensions(file)
        if (width <= MAX_SKIP_DIM && height <= MAX_SKIP_DIM) {
          return file
        }
      } catch (dimErr) {
        // If dimension read fails, continue to standard compression
        console.warn('Could not read image dimensions, proceeding with compression:', dimErr)
      }
    }

    const options = {
      ...DEFAULT_OPTIONS,
      ...customOptions,
    }

    // Perform WebWorker-based canvas resize + EXIF auto-rotation + JPEG encoding
    const compressedBlob = await imageCompression(file, options)

    // Ensure output file has .jpg / .jpeg extension
    const baseName = file.name.replace(/\.[^/.]+$/, '')
    const newFileName = `${baseName}.jpg`

    // Return a standard File instance for direct FormData appending
    return new File([compressedBlob], newFileName, {
      type: 'image/jpeg',
      lastModified: Date.now(),
    })
  } catch (error) {
    console.error(`Failed to compress image "${file.name}":`, error)
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
