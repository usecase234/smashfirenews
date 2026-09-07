<?php
/**
 * The publicist-facing submission page.
 *
 * Phase 3 scope only: paste-text submission, no login, no Turnstile, no
 * rate limiting, no DOCX/PDF/media upload — those are later phases per
 * docs/Smashfire_PR_Starting_Build_Plan.md. "Unlisted" here means a
 * noindexed query-var URL rather than a listed page; Phase 5 is where real
 * abuse prevention lands, not before.
 *
 * The form posts to admin-post.php rather than the REST API so an
 * unauthenticated publicist doesn't need a nonce dance beyond WordPress's
 * normal (works-while-logged-out) nonce support.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class Smashfire_PR_Public_Submission {

	private const QUERY_VAR = 'smashfire_pr_submit';
	private const ACTION    = 'smashfire_pr_submit_release';

	public static function register(): void {
		add_filter( 'query_vars', array( __CLASS__, 'add_query_var' ) );
		add_action( 'template_redirect', array( __CLASS__, 'maybe_render' ) );
		add_action( 'admin_post_' . self::ACTION, array( __CLASS__, 'handle_submit' ) );
		add_action( 'admin_post_nopriv_' . self::ACTION, array( __CLASS__, 'handle_submit' ) );
	}

	public static function add_query_var( array $vars ): array {
		$vars[] = self::QUERY_VAR;
		return $vars;
	}

	public static function maybe_render(): void {
		if ( ! get_query_var( self::QUERY_VAR ) ) {
			return;
		}

		nocache_headers();
		header( 'X-Robots-Tag: noindex, nofollow' );

		if ( isset( $_GET['submitted'] ) ) {
			self::render_confirmation( (int) $_GET['submitted'] );
		} else {
			self::render_form( isset( $_GET['error'] ) ? sanitize_text_field( wp_unslash( $_GET['error'] ) ) : null );
		}
		exit;
	}

	private static function render_form( ?string $error ): void {
		?>
		<!doctype html>
		<html>
		<head><meta charset="utf-8"><title>Submit a release</title></head>
		<body>
			<h1>Submit a release</h1>
			<?php if ( $error ) : ?>
				<p style="color:red;"><?php echo esc_html( $error ); ?></p>
			<?php endif; ?>
			<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
				<?php wp_nonce_field( self::ACTION ); ?>
				<input type="hidden" name="action" value="<?php echo esc_attr( self::ACTION ); ?>">
				<p><label>Headline<br><input type="text" name="headline" required></label></p>
				<p><label>Release text<br><textarea name="body_text" rows="12" cols="60" required></textarea></label></p>
				<p><label>Your name<br><input type="text" name="sender_name" required></label></p>
				<p><label>Your email<br><input type="email" name="sender_email" required></label></p>
				<p><label>Company/label/agency<br><input type="text" name="sender_company"></label></p>
				<p><button type="submit">Submit</button></p>
			</form>
		</body>
		</html>
		<?php
	}

	private static function render_confirmation( int $submission_id ): void {
		?>
		<!doctype html>
		<html>
		<head><meta charset="utf-8"><title>Submission received</title></head>
		<body>
			<h1>Thanks — we've got it.</h1>
			<p>Submission ID: <?php echo esc_html( (string) $submission_id ); ?></p>
			<p>This does not guarantee publication. If a duplicate of a prior submission, it may be merged or rejected during review.</p>
		</body>
		</html>
		<?php
	}

	public static function handle_submit(): void {
		check_admin_referer( self::ACTION );

		$headline        = sanitize_text_field( wp_unslash( $_POST['headline'] ?? '' ) );
		$body_text       = sanitize_textarea_field( wp_unslash( $_POST['body_text'] ?? '' ) );
		$sender_name     = sanitize_text_field( wp_unslash( $_POST['sender_name'] ?? '' ) );
		$sender_email    = sanitize_email( wp_unslash( $_POST['sender_email'] ?? '' ) );
		$sender_company  = sanitize_text_field( wp_unslash( $_POST['sender_company'] ?? '' ) );

		if ( '' === $headline || '' === $body_text || '' === $sender_name || ! is_email( $sender_email ) ) {
			self::redirect_back( array( 'error' => 'Please fill in headline, release text, your name and a valid email.' ) );
		}

		$hub    = new Smashfire_Hub_Client();
		$result = $hub->submit_release(
			array(
				'headline'       => $headline,
				'body_text'      => $body_text,
				'sender_name'    => $sender_name,
				'sender_email'   => $sender_email,
				'sender_company' => '' !== $sender_company ? $sender_company : null,
			)
		);

		if ( is_wp_error( $result ) || empty( $result['id'] ) ) {
			self::redirect_back( array( 'error' => 'Sorry, something went wrong submitting your release. Please try again.' ) );
		}

		self::redirect_back( array( 'submitted' => $result['id'] ) );
	}

	/**
	 * Sends the browser back to the submission page with the given query
	 * args and exits — every call site above treats this as terminal.
	 */
	private static function redirect_back( array $args ): void {
		$url = add_query_arg( array_merge( array( self::QUERY_VAR => 1 ), $args ), home_url( '/' ) );
		wp_safe_redirect( $url );
		exit;
	}
}
