# Custom Jekyll plugin to get Git commit dates for files
#
# Usage:
#   {{ "path/to/file" | file_date }}                    # Returns: 2025年09月
#   {{ "_data/member.csv" | file_date: "%Y-%m-%d" }}    # Returns: 2025-09-26
#   {{ "some/file.txt" | file_date: "%B %Y" }}          # Returns: September 2025
#
# The filter accepts relative paths from the site root.
# Returns the date of the last Git commit that modified the file.
# Falls back to file modification time if Git is not available or file is not tracked.
# Returns empty string if file doesn't exist.
module Jekyll
  module FileDateFilter
    def file_date(input, format = "%Y年%m月")
      return "" unless input

      # Build path relative to site root
      file_path = File.join(@context.registers[:site].source, input)

      return "" unless File.exist?(file_path)

      # Try to get Git commit date, fall back to file mtime
      begin
        git_date = `git log -1 --format=%ct -- "#{file_path}" 2>/dev/null`.strip

        if !git_date.empty? && git_date.match?(/^\d+$/)
          # Convert Unix timestamp to Time object and format
          return Time.at(git_date.to_i).strftime(format)
        end
      rescue
        # Git command failed, go to fallback
      end

      File.mtime(file_path).strftime(format)
    end
  end
end

# Register the filter with Liquid template engine
Liquid::Template.register_filter(Jekyll::FileDateFilter)