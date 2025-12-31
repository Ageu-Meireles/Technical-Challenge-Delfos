--
-- PostgreSQL database dump
--

\restrict 4hFK4JUwayd27NLgPM3lYFL25TyU4oQHabneDlB67zPSkddCOZHg8IgxcDiAjw6

-- Dumped from database version 16.11
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: delfos
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO delfos;

--
-- Name: data; Type: TABLE; Schema: public; Owner: delfos
--

CREATE TABLE public.data (
    "timestamp" timestamp without time zone NOT NULL,
    signal_id integer NOT NULL,
    value double precision NOT NULL
);


ALTER TABLE public.data OWNER TO delfos;

--
-- Name: signal; Type: TABLE; Schema: public; Owner: delfos
--

CREATE TABLE public.signal (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.signal OWNER TO delfos;

--
-- Name: signal_id_seq; Type: SEQUENCE; Schema: public; Owner: delfos
--

CREATE SEQUENCE public.signal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.signal_id_seq OWNER TO delfos;

--
-- Name: signal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: delfos
--

ALTER SEQUENCE public.signal_id_seq OWNED BY public.signal.id;


--
-- Name: signal id; Type: DEFAULT; Schema: public; Owner: delfos
--

ALTER TABLE ONLY public.signal ALTER COLUMN id SET DEFAULT nextval('public.signal_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: delfos
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: data data_pkey; Type: CONSTRAINT; Schema: public; Owner: delfos
--

ALTER TABLE ONLY public.data
    ADD CONSTRAINT data_pkey PRIMARY KEY ("timestamp", signal_id);


--
-- Name: signal signal_pkey; Type: CONSTRAINT; Schema: public; Owner: delfos
--

ALTER TABLE ONLY public.signal
    ADD CONSTRAINT signal_pkey PRIMARY KEY (id);


--
-- Name: ix_signal_name; Type: INDEX; Schema: public; Owner: delfos
--

CREATE UNIQUE INDEX ix_signal_name ON public.signal USING btree (name);


--
-- Name: data data_signal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: delfos
--

ALTER TABLE ONLY public.data
    ADD CONSTRAINT data_signal_id_fkey FOREIGN KEY (signal_id) REFERENCES public.signal(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 4hFK4JUwayd27NLgPM3lYFL25TyU4oQHabneDlB67zPSkddCOZHg8IgxcDiAjw6

