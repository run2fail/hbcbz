hbcbz
=====

Simple Python scripts to cleanup comic book zip (CBZ) archives downloaded from
Humble Bundle.

While Humble Bundle often times offers interesting ebook bundles, the provided
CBZ files need some fixing:

- Some archives contain duplicates
- Downloaded files have annoying suffixes
- The average size of the contained images can be pretty large which results in
  large archive files
- Some images are even 20 MB JPEGs that are 16,000 px wide which cannot be
  handled by resource contrained systems (tablets, smart phones, ...)

In one extreme case the downloaded CBZ file could be reduced from 85 MB down to
6.5 MB. Yes this is mostly due to the lossy compression / resizing of the images
but HD resolution is usually sufficient.
