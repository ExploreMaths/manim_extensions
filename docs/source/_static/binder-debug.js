(function() {
    console.log('[manim-ext] ===== Binder Debug START =====');
    console.log('[manim-ext] Page URL:', window.location.href);
    console.log('[manim-ext] Repo: ExploreMaths/manim_extensions, Branch: main');

    var binders = document.querySelectorAll('[data-manim-binder]');
    console.log('[manim-ext] Found ' + binders.length + ' [data-manim-binder] elements');
    binders.forEach(function(el, i) {
        var cn = el.getAttribute('data-manim-classname') || '(no classname)';
        console.log('[manim-ext]   #' + i + ': classname=' + cn);
    });

    if (typeof window.initManimBinder === 'function') {
        console.log('[manim-ext] initManimBinder function exists, calling...');
        try {
            window.initManimBinder({
                repo: 'ExploreMaths/manim_extensions',
                branch: 'main',
                storage_expire: 0
            });
            console.log('[manim-ext] initManimBinder() returned successfully');
        } catch(e) {
            console.error('[manim-ext] initManimBinder() FAILED:', e);
        }
    } else {
        console.error('[manim-ext] initManimBinder is NOT defined on window!');
        console.error('[manim-ext] manim-binder.min.js may not have loaded.');
    }

    console.log('[manim-ext] ===== Binder Debug END =====');
})();