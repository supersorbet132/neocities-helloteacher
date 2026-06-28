# Portfolio site feature planning

### Folder Hierarchy:

neocities-helloteacher/  
├── index.html  
├── kombucha.css  
├── robots.txt  
├── not\_found.html  
├── about/  
│   └── index.html  
├── art/  
│   └── index.html  
├── cad/  
│   └── index.html  
├── journal/  
│   └── index.html  
└── assets/  
    ├── images/  
    │   └── site/  
    │       └── neocities.png  
    └── js/  
        └── main.js

### Current state:

- Five pages are present. The homepage is empty (contains placeholder information from the template), art, cad, about and journal each also contain an empty template.   
- Links between art, cad, about and journal work. Homepage contains no links.  
- Kombucha.css is unmodified. No js behavior has been defined.   
- Assets folder is mostly empty, save for js, which contains an empty js file, and the site folder under images, which contains the default neocities image.

### Goals (reference regularly):

- Create legible, clean code that is easy to maintain in the future.  
- Carefully craft features that work modularly. Pages should be able to operate in a vacuum at all times.  
- Reference existing conventions and always suggest features/techniques that could simplify a process.  
- Review new features thoroughly.

## Planned features:

### Overall

- Common page footer with navigation links (to each main page), credits for the template and neocities, and some links to my socials/my name.

### Homepage

- Cosmetic modifications to the homepage  
- Architecture allowing for custom images, gifs, etc. to populate the screen  
- Info cards that provide a preview for/lead to each page

### Art

- Gallery view with flexible positioning (so that image positions and scale can be animated in the future)  
- Js lightbox framework to display artworks without leading to a new page  
- Framework that allows for new artworks to be added easily  
- Sections of the gallery where I can display custom parallax artworks (leave blank, cosmetic feature)

### Cad

- Gallery view of CAD models. CAD models would be previewed within interactive cards, akin to the homepage. Models should have a framework allowing for animation.  
- As of now, I am unsure what the best way to approach viewing models is. I would prefer not to redirect the user for every model visited, but it might be necessary for more complicated projects. Ideally, the user should be able to browse models, view details, and exit all on the same page. 

### Journal

- Gallery view of journal entry previews (entries should be in the form of card views, akin to the way items are displayed on the main page).   
- Clicking on a journal entry would enlarge said entry on the same page (avoid finicky navigation).  
- Framework that allows for easily adding new journal entries.  
- Journal entries should support images and text.

### About

- Fairly barebones page. Doesn’t need to do much besides support images and text. For now, we will leave this as a brief descriptor of the site as a whole (which I will handle). I might come back to this page in the future to add cosmetic features.